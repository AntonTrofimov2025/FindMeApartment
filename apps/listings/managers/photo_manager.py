from django.db import models
from django.utils import timezone



class PhotoSoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet layer enabling atomic soft-deletion for property media entries.
    """
    def delete(self):
        return self.update(deleted_at=timezone.now())


class PhotoSoftDeleteManager(models.Manager):
    """
    Default media manager filtering out soft-deleted photo entries from production queries.
    """
    def get_queryset(self):
        return PhotoSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

