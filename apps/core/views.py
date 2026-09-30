from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny



@extend_schema(summary='Exception Handler Test',
               description='Assurance of proper working of custom django standard exceptions handler.',
               tags=['Testing / System'],
               request=None,
               responses={
                   500: OpenApiResponse(
                       description="Standardized 500 Server Error JSON response triggered by ZeroDivisionError.")
               })
@api_view(['GET'])
@permission_classes([AllowAny])
def test_django_standard_exceptions(request):
    """
    System endpoint designed to trigger a ZeroDivisionError.

    Used exclusively in test and staging environments to verify that
    the global drf_standardized_err_custom_exception_handler intercepts
    core Python/Django exceptions and cleanly converts them into
    standardized 500 Server Error JSON responses.
    """
    x = 1 / 0
    return Response({'msg': x})

@extend_schema(
    summary="System Health Check",
    description="Provides container orchestration tools with a simple mechanism to verify that the application instance is live.",
    tags=['Testing / System'],
    request=None,
    responses={
        200: OpenApiResponse(description="Server works fine :)")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Lightweight health check endpoint.

    Provides container orchestration tools (like Docker compose healthchecks or AWS ECS)
    with a simple mechanism to verify that the Gunicorn/Django application
    instance is live, responsive, and accepting incoming HTTP traffic.
    """
    return Response("Server works fine :)", status=HTTP_200_OK)

