from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_birth_date(value):
    if not value:
        return

    today = timezone.localdate()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

    if age < 18:
        raise ValidationError(_('You must be at least 18 years old to register!'))

    if age > 120:
        raise ValidationError(_('You are so old my friend! :D Try again :)'))

