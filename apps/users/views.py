from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .serializers.users import UserListSerializer, RegisterUserSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer

@extend_schema(summary='Register new user', description='New user registration')
class UserCreateGenericView(CreateAPIView):

    queryset = get_user_model().all_objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

class UserMeView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user's profile.", responses={'200': UserListSerializer},
                   tags=["User Profile"])
    def get(self, request, *args, **kwargs):
        serializer = UserListSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Fully updates current user's profile (such as avatar, phone number, etc.)", request=RegisterUserSerializer,
                   responses={'200': UserListSerializer}, tags=["User Profile"])
    def put(self, request, *args, partial=False, **kwargs):
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
        request.user.delete()
        return Response(
            {'msg': "Your account has been successfully deleted. We'd like to kindly thank you for being with us! :)"},
            status=status.HTTP_200_OK
        )

class UserBecomeLandlordView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Become a Landlord",
        description="Switch current user group from Tenant to Landlord to allow property listing.",
        responses={'200': 'Successfully became a landlord.'},
        tags=["User Profile"]
    )
    def post(self, request, *args, **kwargs):
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
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'msg': 'You have been logged out.'}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({'detail': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)


class UserReadOnlyViewSet(ReadOnlyModelViewSet):

    queryset = get_user_model().all_objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

# class LogOutApiView(GenericAPIView):
#
#     permission_classes = [IsAuthenticated]
#     serializer_class = TokenBlacklistSerializer
#
#     @extend_schema(summary='Account Logout',
#                    description='Logout authorized user by putting his REFRESH TOKEN to BLACKLIST.',
#                    responses={
#                        status.HTTP_200_OK: 'You have been logged out.',
#                        status.HTTP_401_UNAUTHORIZED: 'You have not been logged in.'
#                    })
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         refresh_token = request.data.get('refresh')
#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response({'msg': 'You have been logged out.'}, status=status.HTTP_200_OK)
#         except TokenError:
#             return Response({'detail': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)


