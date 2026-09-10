from django.db import models
from django.utils import timezone



class PhotoSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())


class PhotoSoftDeleteManager(models.Manager):
    def get_queryset(self):
        return PhotoSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

