from django.db import models
from django.utils import timezone


class BookingsSoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet layer providing automated soft-delete operations for groups of bookings.
    """
    def delete(self):
        return self.update(deleted_at=timezone.now())


class BookingsSoftDeleteManager(models.Manager):
    """
    Default manager for the Booking model that automatically filters out soft-deleted records.

    Ensures that queries executed via `Booking.objects` only look up active, non-archived reservations.
    """
    def get_queryset(self):
        return BookingsSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

