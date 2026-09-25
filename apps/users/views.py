from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from .serializers.users import UserListSerializer, RegisterUserSerializer, ChangePasswordSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, APIView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer

@extend_schema(summary='Register new user', description='New user registration')
class UserCreateGenericView(CreateAPIView):
    """
    Endpoint for public tenant registration.

    Accepts registration details, performs password validation constraints,
    and checks if the email is already taken against both active and soft-deleted accounts.
    Automatically assigns the new user to the default 'Tenant' group upon creation.
    """

    queryset = get_user_model().all_objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

class UserMeView(APIView):
    """
    A unified profile management controller for the currently authenticated user.

    Provides direct access to personal data, profile updating flows, and safe account closure.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user's profile.", responses={'200': UserListSerializer},
                   tags=["User Profile"])
    def get(self, request, *args, **kwargs):
        """
        Retrieve personal profile summary.

        Returns full details of the authenticated user instance, including relation metadata,
        phone state, and system timestamps.
        """
        serializer = UserListSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Securely change current user's password",
        request=ChangePasswordSerializer,
        responses={"200": "Password changed successfully."},
        tags=["User Profile"]
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Secure password mutation endpoint.
        Verifies historic token context, updates the cryptographic pbkdf2 hash,
        and blacklists the previous session context if necessary.
        """
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])

        old_refresh = serializer.validated_data['refresh']
        try:
            token = RefreshToken(old_refresh)
            token.blacklist()
        except TokenError:
            raise ValidationError({'refresh': 'Provided refresh token is invalid or already expired.'})

        refresh = RefreshToken.for_user(user)

        user.save(update_fields=['password'])
        return Response({'msg': 'Password has been successfully updated.',
                             'tokens': {
                                 'refresh': str(refresh),
                                 'access': str(refresh.access_token)
                             }}, status=status.HTTP_200_OK)

    @extend_schema(summary="Fully updates current user's profile (such as avatar, phone number, etc.)", request=RegisterUserSerializer,
                   responses={'200': UserListSerializer}, tags=["User Profile"])
    def put(self, request, *args, partial=False, **kwargs):
        """
        Perform a full or partial data synchronization for the user's profile.

        Handles phone formatting syntax checks, unique email validation, excludes
        and accepts profile updates without password re-entry on partial fields payload.
        """
        serializer = RegisterUserSerializer(request.user, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserListSerializer(request.user, context={'request': request}).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Partially updates current user's profile (such as avatar, phone number, etc.)",
                   request=RegisterUserSerializer,
                   responses={'200': UserListSerializer}, tags=["User Profile"])
    def patch(self, request, *args, **kwargs):
        return self.put(request, partial=True)

    @extend_schema(
        summary="Delete current user's account",
        description="Soft deletes the authenticated user profile, deactivates access, and logs the timestamp.",
        responses={"200": "Your account has been successfully deleted."},
        tags=["User Profile"]
    )
    def delete(self, request, *args, **kwargs):
        """
        Trigger soft-deletion flow for the authenticated user's account.

        Deactivates profile visibility flag (`is_active=False`) and logs the deletion
        timestamp (`deleted_at`), completely blocking future authentication attempts
        under these credentials without hard-deleting the underlying transactional data logs.
        """
        request.user.delete()
        return Response(
            {'msg': "Your account has been successfully deleted. We'd like to kindly thank you for being with us! :)"},
            status=status.HTTP_200_OK
        )

class UserBecomeLandlordView(APIView):
    """
    Controller to handle privilege elevation requests for Tenants.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Become a Landlord",
        description="Switch current user group from Tenant to Landlord to allow property listing.",
        responses={'200': 'Successfully became a landlord.'},
        tags=["User Profile"]
    )
    def post(self, request, *args, **kwargs):
        """
        Upgrade the user's role from Tenant to Landlord.

        Removes the user from the system 'Tenant' group and re-assigns them to the 'Landlord' group.
        Instantly generates and issues a fresh set of JWT Access and Refresh tokens with updated claims
        to avoid forced application re-login cycles on the frontend UI layer.
        """
        user = request.user

        if user.groups.filter(name='Landlord').exists():
            return Response({'detail': 'You are already a Landlord!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tenant_group = Group.objects.get(name='Tenant')
            landlord_group = Group.objects.get(name='Landlord')
            user.groups.remove(tenant_group)
            user.groups.add(landlord_group)
            refresh = RefreshToken.for_user(user)

            return Response({'msg': 'You are now a Landlord. You can host properties! :)',
                             'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)}},
                            status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            return Response({'detail': 'System user groups (Tenant/Landlord) are not initialized.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(summary='Account Logout',
               description='Logout authorized user by putting his REFRESH TOKEN to BLACKLIST.',
               responses={
                   "200": 'You have been logged out.',
                   "401": 'You have not been logged in.'
               },
               request=TokenBlacklistSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request, *args, **kwargs):
    """
    Revoke user session and invalidate authentication tokens.

    Accepts a valid JWT Refresh token, performs validation parsing, and pushes it
    into the Django security token blacklist database registry to complete the session termination flow.
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        raise ValidationError({'detail': 'Refresh token is required.'})
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'msg': 'You have been logged out.'}, status=status.HTTP_200_OK)
    except TokenError:
        raise ValidationError({'detail': 'Token is invalid or expired.'})


class UserReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    Administrative directory ViewSet for monitoring user profiles.

    Provides high-privilege read-only list and detail lookups.
    Leverages the `all_objects` model manager to keep soft-deleted user records
    visible for compliance audits, analytical cross-matching, and historical tracking.
    """

    queryset = get_user_model().all_objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]


