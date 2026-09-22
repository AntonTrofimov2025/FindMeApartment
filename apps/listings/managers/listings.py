from django.db import models
from django.utils import timezone



class ListingsSoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet layer enabling atomic batch soft-deletion on sets of property listings.
    """
    def delete(self):
        return self.update(deleted_at=timezone.now())


class ListingsSoftDeleteManager(models.Manager):
    """
    Default property manager that restricts standard database queries to non-deleted listings.
    """
    def get_queryset(self):
        return ListingsSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

