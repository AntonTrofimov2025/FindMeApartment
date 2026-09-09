from django.db import models
from django.utils import timezone


class ReviewsSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())


class ReviewsSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return ReviewsSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

