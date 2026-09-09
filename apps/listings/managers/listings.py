from django.db import models
from django.utils import timezone


# class ListingSoftDeleteManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)

class ListingSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())


class ListingSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return ListingSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

