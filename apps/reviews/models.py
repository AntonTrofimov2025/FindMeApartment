from django.db import models
from apps.listings.models import Listing
from apps.core.models import UniqueID, TimeStampedModel
from .managers.reviews import ReviewsSoftDeleteManager
from django.utils import timezone
from apps.bookings.models import Booking
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q


class Review(UniqueID, TimeStampedModel):

    booking = models.OneToOneField(Booking, related_name='review', on_delete=models.PROTECT,
                                help_text='Associated Booking', verbose_name=_('Booking'))

    property_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    location_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(max_length=1500, help_text=_("Review's text"), verbose_name=_("Review's text"))

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    objects = ReviewsSoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'fma_reviews'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        ordering = ('-created_at',)
        constraints = [models.CheckConstraint(name='property_rating_1_to_5',
                                              condition=Q(property_rating__gte=1) & Q(property_rating__lte=5),
                                              violation_error_message='Property rating must be between 1 and 5!'),
                       models.CheckConstraint(name='location_rating_1_to_5',
                                              condition=Q(location_rating__gte=1) & Q(location_rating__lte=5),
                                              violation_error_message='Location rating must be between 1 and 5!')
                       ]

