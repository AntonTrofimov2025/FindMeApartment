from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from .serializers.users import UserListSerializer, RegisterUserSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer

@extend_schema(summary='Register new user', description='New user registration')
class UserCreateGenericView(CreateAPIView):

    queryset = get_user_model().all_objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    # def get_queryset(self):
    #     if project := self.request.query_params.get('project'):
    #         return self.queryset.filter(project__name=project)
    #     return self.queryset

@extend_schema(summary='Account Logout',
               description='Logout authorized user by putting his REFRESH TOKEN to BLACKLIST.',
               responses={
                   status.HTTP_200_OK: 'You have been logged out.',
                   status.HTTP_401_UNAUTHORIZED: 'You have not been logged in.'
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


class UserReadOnlyGenericView(ReadOnlyModelViewSet):

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


