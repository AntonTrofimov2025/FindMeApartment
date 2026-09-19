from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny



@extend_schema(summary='Exception Handler Test',
               description='Assurance of proper working of custom django standard exceptions handler.',
               tags=['Testing / System'])
@api_view(['GET'])
@permission_classes([AllowAny])
def test_django_standard_exceptions(request):
    x = 1 / 0
    return Response({'msg': x})

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response("Server works fine :)", status=HTTP_200_OK)

