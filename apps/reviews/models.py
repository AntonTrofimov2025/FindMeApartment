from django.db import models
from apps.listings.models import Listing
from apps.core.models import UniqueID, TimeStampedModel
from .managers.reviews import ReviewsSoftDeleteManager
from django.utils import timezone
from apps.bookings.models import Booking
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from apps.core.models import StatusChoices
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class Review(UniqueID, TimeStampedModel):
    """
    Database model representing tenant feedback and structural ratings.

    Maintains a strict One-to-One structural mapping with a single completed Booking instance.
    Stores qualitative text entries alongside standardized numeric evaluation scales.

    Business Rules Enforced:
        - Prevents reviews from being published until the target booking status is officially 'COMPLETED'.
        - Relies on database check constraints to enforce property and location metrics between 1 and 5 stars.
    """
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
        super().save(update_fields=['deleted_at', 'updated_at'])

    def clean(self):
        super().clean()
        try:
            if not self.booking_id:
                return
        except ObjectDoesNotExist:
            return
        if self.booking.booking_status != StatusChoices.COMPLETED:
            raise ValidationError(_('You can only leave a review after the booking is completed!'))

    def save(self, *args, **kwargs):
        try:
            if not self.booking_id:
                return
        except ObjectDoesNotExist:
            return
        self.full_clean()
        super().save(*args, **kwargs)

    objects = ReviewsSoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Review from user: {self.booking.user_id}"

    def __repr__(self):
        return (f"<Review(booking={self.booking_id}, text={self.text}, property_rating={self.property_rating},"
                f" location_rating={self.location_rating})>")

    class Meta:
        db_table = 'fma_reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)
        constraints = [models.CheckConstraint(name='property_rating_1_to_5',
                                              condition=Q(property_rating__gte=1) & Q(property_rating__lte=5),
                                              violation_error_message=_('Property rating must be between 1 and 5!')),
                       models.CheckConstraint(name='location_rating_1_to_5',
                                              condition=Q(location_rating__gte=1) & Q(location_rating__lte=5),
                                              violation_error_message=_('Location rating must be between 1 and 5!'))
                       ]
        indexes = [models.Index(fields=['-created_at'], name='fma_reviews_created_at_idx'),
                   models.Index(fields=['property_rating', 'location_rating'], name='fma_reviews_prop_loc_rat_idx'),
                   models.Index(fields=['property_rating'], name='fma_reviews_prop_rating_idx'),
                   models.Index(fields=['location_rating'], name='fma_reviews_loc_rating_idx'),
                   models.Index(fields=['booking'], name='fma_reviews_booking_id_idx')]



