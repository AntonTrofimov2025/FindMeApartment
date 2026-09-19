from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from drf_standardized_errors.handler import exception_handler


def drf_standardized_err_custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        elif hasattr(exc, 'messages'):
            errors = exc.messages
        else:
            errors = str(exc)
        exc = ValidationError(errors)

    return exception_handler(exc, context)

