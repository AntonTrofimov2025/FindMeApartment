from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from drf_standardized_errors.handler import ExceptionHandler

class CustomDRFStandardizedErrorsExceptionHandler(ExceptionHandler):
    """
    Global exception converter hook integrated with drf-standardized-errors.

    Intercepts standard Django-core model ValidationErrors (thrown during full_clean processes)
    and shifts them into native Django REST Framework ValidationError instances.
    Prevents unhandled model level issues from triggering catastrophic 500 Server Errors,
    seamlessly responding with clear, standardized 400 Client Request JSON structures instead.
    """

    def convert_known_exceptions(self, exc: Exception) -> Exception:
        if isinstance(exc, DjangoValidationError):
            if hasattr(exc, 'message_dict'):
                errors = exc.message_dict
            elif hasattr(exc, 'messages'):
                errors = exc.messages
            else:
                errors = str(exc)
            exc = ValidationError(errors)

        return super().convert_known_exceptions(exc)

# def drf_standardized_err_custom_exception_handler(exc, context):
#     if isinstance(exc, DjangoValidationError):
#         if hasattr(exc, 'message_dict'):
#             errors = exc.message_dict
#         elif hasattr(exc, 'messages'):
#             errors = exc.messages
#         else:
#             errors = str(exc)
#         exc = ValidationError(errors)
#
#     return exception_handler(exc, context)
#
