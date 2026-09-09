from django.db import models
from django.utils import timezone


class BookingsSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())


class BookingsSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return BookingsSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

