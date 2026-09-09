from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import UniqueID, TimeStampedModel
from django.utils import timezone
from .managers.bookings import BookingsSoftDeleteManager


class Booking(UniqueID, TimeStampedModel):
    date_from = models.DateField()
    date_to = models.DateField()

    objects = BookingsSoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def clean(self):
        super().clean()
        if self.date_to and self.date_from and self.date_to <= self.date_from:
            raise ValidationError('Booking start date can not be greater than end date!')

    # WORK IN PROGRESS

