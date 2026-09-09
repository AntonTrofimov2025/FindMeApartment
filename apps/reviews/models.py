from django.db import models
from apps.listings.models import Listing
from apps.core.models import UniqueID, TimeStampedModel
from .managers.reviews import ReviewsSoftDeleteManager
from django.utils import timezone


class Review(UniqueID, TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='reviews', verbose_name='Listing')

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    objects = ReviewsSoftDeleteManager()
    all_objects = models.Manager()

    # WORK IN PROGRESS