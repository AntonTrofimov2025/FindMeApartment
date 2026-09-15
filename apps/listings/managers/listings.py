from django.db import models
from django.utils import timezone


# class ListingsSoftDeleteManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)

class ListingsSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())


class ListingsSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return ListingsSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

