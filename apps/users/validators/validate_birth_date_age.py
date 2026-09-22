from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_birth_date(value):
    """
    Chronological validation logic for user birth dates.

    Calculates the exact age delta in years between the provided birth date
    and the current server local time. Enforces systemic bounds to legally restrict
    registrations to adults (>= 18 years) and reject anomalous profiles (> 120 years).
    """
    if not value:
        return

    today = timezone.localdate()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

    if age < 18:
        raise ValidationError(_('You must be at least 18 years old to register!'))

    if age > 120:
        raise ValidationError(_('You are so old my friend! :D Try again :)'))

