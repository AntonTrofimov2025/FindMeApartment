from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import UniqueID, TimeStampedModel
from apps.listings.models import Listing
from django.utils import timezone
from .managers.bookings import BookingsSoftDeleteManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import StatusChoices
from decimal import Decimal



class Booking(UniqueID, TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings', verbose_name=_('Listing'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings',
                                verbose_name=_('User'))

    date_from = models.DateField()
    date_to = models.DateField()

    booking_status = models.CharField(choices=StatusChoices, default=StatusChoices.PENDING, max_length=15,
                                      help_text="Shows current booking's status", verbose_name=_("Booking's status"))
    guests_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                              help_text="Specified guests number", verbose_name=_("Guest number"))

    snapshot_data = models.JSONField(blank=True, verbose_name=_('Snapshot of current Listing data'))

    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      help_text='Total price for the stay', verbose_name=_('Total price'))

    objects = BookingsSoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def clean(self):
        super().clean()
        if self.date_to and self.date_from and self.date_to <= self.date_from:
            raise ValidationError('Booking start date can not be greater than end date!')
        if (Booking.objects.filter(listing_id=self.listing_id, booking_status__in=[StatusChoices.PENDING, StatusChoices.CONFIRMED],
                                  date_from__lt=self.date_to, date_to__gt=self.date_from).
                exclude(id__in=[self.pk] if self.pk else []).exists()):
            raise ValidationError("Unfortunately the selected dates are already booked.")

    def save(self, *args, **kwargs):

        if self.date_to and self.date_from and self.listing:
            nights = (self.date_to - self.date_from).days
            self.total_price = nights * self.listing.price_per_night if nights > 0 else Decimal("0.00")

        self.full_clean()

        if not self.pk:
            snapshot_data = {}

            if self.user:
                snapshot_data['tenant'] = {
                    'email': self.user.email or "No data",
                    'phone': self.user.phone or "No data",
                    'first_name': self.user.first_name or "No data",
                    'last_name': self.user.last_name or "No data",
                    'birth_date': str(self.user.birth_date) if self.user.birth_date else "No data",
                }

            if self.listing:
                snapshot_data['property_data'] = {
                    'title': self.listing.title or "No data",
                    'country': self.listing.get_country_display() or "No data",
                    'district': self.listing.district or "No data",
                    'city': self.listing.city or "No data",
                    'street': self.listing.street or "No data",
                    'house_number': self.listing.house_number or "No data",
                    'apartment_number': self.listing.apartment_number or "No data",
                    'max_guests': self.listing.get_max_guests_display() or "No data",
                    'property_type': self.listing.get_property_type_display() or "No data",
                    'price_per_night': str(self.listing.price_per_night) if self.listing.price_per_night is not None
                    else "No data",
                    'rooms': self.listing.get_rooms_display() or "No data",
                }
            if self.total_price:
                snapshot_data['total_price'] = self.total_price

            self.snapshot_data = snapshot_data
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking's Title: {self.listing.title}"

    def __repr__(self):
        return (f"<Booking(date_from={self.date_from}, user={self.user}, date_to={self.date_to},"
                f" booking_status={self.booking_status}, guests_number={self.guests_number},"
                f" total_price={self.total_price})>")

    class Meta:
        db_table = 'fma_bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ('-created_at',)
        constraints = [models.CheckConstraint(name='guests_from_1_to_10',
                                              condition=Q(guests_number__gte=1) & Q(guests_number__lte=10),
                                              violation_error_message='Guests number must be between 1 and 10!'),
                       models.CheckConstraint(name='start_date_gt_than_end_date',
                                              condition=Q(date_to__gt=F('date_from')),
                       violation_error_message='Booking start date can not be greater than end date!')]

