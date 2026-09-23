from django.db import models, transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from simple_history.models import HistoricalRecords



class Booking(UniqueID, TimeStampedModel):
    """
    Database model representing a property reservation transaction.

    Maintains the full lifecycle of a rental agreement between a Tenant and a Landlord.
    Calculates final pricing dynamically based on listing discounts and stay duration.
    Captures an immutable, frozen data snapshot (`snapshot_data`) upon creation or date modification
    to preserve historical financial and legal logs against subsequent profile updates.

    Business Rules Enforced:
        - Strict chronologically valid date ranges (check-out must succeed check-in).
        - Double-booking prevention via non-overlapping reservation checking filters.
        - Advanced limits: Maximum 30-night stays, no bookings more than 1 year in advance.
        - Operational safeguards: Prevent check-in before the target arrival date,
          and restrict standard cancellations to a minimum of 2 days prior to check-in.
    """
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings', verbose_name=_('Listing'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings',
                                verbose_name=_('User'))

    date_from = models.DateField()
    date_to = models.DateField()

    booking_status = models.CharField(choices=StatusChoices, default=StatusChoices.PENDING, max_length=15,
                                      help_text="Shows current booking's status", verbose_name=_("Booking's status"))
    guests_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                              help_text="Specified guests number", verbose_name=_("Guest number"))

    snapshot_data = models.JSONField(default=dict, verbose_name=_('Snapshot of current Listing data'))

    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      help_text='Total price for the stay', verbose_name=_('Total price'),
                                      validators=[MinValueValidator(Decimal('0.00'))])
    history = HistoricalRecords(
        table_name='fma_bookings_historicalrecords'
    )

    objects = BookingsSoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        super().save(update_fields=['deleted_at', 'updated_at'])

    def clean(self):
        super().clean()
        try:
            if not self.listing or not self.user_id:
                return
        except ObjectDoesNotExist:
            return
        if self.date_to and self.date_from and self.date_to <= self.date_from:
            raise ValidationError(_('Booking start date can not be greater than end date!'))
        if (Booking.objects.filter(listing_id=self.listing_id,
                                   booking_status__in=[StatusChoices.PENDING, StatusChoices.CONFIRMED,
                                                       StatusChoices.CHECKED_IN, StatusChoices.COMPLETED],
                                  date_from__lt=self.date_to, date_to__gt=self.date_from).
                exclude(id__in=[self.pk] if self.pk else []).exists()):
            raise ValidationError(_("Unfortunately the selected dates are already booked."))

        if self.date_from and self.date_from < timezone.localdate():
            raise ValidationError(_('Booking start date cannot be in the past.'))
        if self.date_from and self.date_from > timezone.localdate() + relativedelta(years=1):
            raise ValidationError(_('You cannot book more than 1 year in advance.'))
        if self.date_to and self.date_to > timezone.localdate() + relativedelta(years=1):
            raise ValidationError(_('Booking end date cannot exceed 1 year from today.'))
        if self.date_from and self.date_to and (self.date_to - self.date_from).days > 30:
            raise ValidationError(_("You cannot book this property for more than 30 nights."))

        if self.guests_number is not None and self.guests_number > self.listing.max_guests:
            raise ValidationError(_(f"The number of guests cannot exceed the listing's maximum capacity. (max: {self.listing.max_guests})"))

        if self.booking_status == StatusChoices.CANCELLED:
            if self.pk:
                booking = Booking.objects.get(pk=self.pk)

                if booking.booking_status == StatusChoices.CONFIRMED:
                    if timezone.localdate() > self.date_from - timedelta(days=2):
                        raise ValidationError(_('You cannot cancel this booking less than 2 days before the start date.'))


    def save(self, *args, **kwargs):
        try:
            if not self.listing or not self.user_id:
                return
        except ObjectDoesNotExist:
            return
        with transaction.atomic():
            selected_listing = Listing.all_objects.select_for_update().get(pk=self.listing_id)

            dates_changed = False
            if self.pk:
                old_dates = Booking.all_objects.filter(pk=self.pk).values('date_from', 'date_to').first()
                if old_dates and (old_dates['date_from'] != self.date_from or old_dates['date_to'] != self.date_to):
                    dates_changed = True

            if self.date_to and self.date_from and selected_listing:
                if self._state.adding or dates_changed:
                    nights = (self.date_to - self.date_from).days
                    self.total_price = nights * selected_listing.final_price_per_night if nights > 0 else Decimal("0.00")

            if self._state.adding or dates_changed:
                snapshot_data = {'Tenant': {
                    'email': self.user.email or "No data",
                    'phone': self.user.phone or "No data",
                    'first_name': self.user.first_name or "No data",
                    'last_name': self.user.last_name or "No data",
                    'birth_date': str(self.user.birth_date) if self.user.birth_date else "No data",
                }}

                if self.listing:
                    snapshot_data['property_data'] = {
                        'title': selected_listing.title or "No data",
                        'country': selected_listing.get_country_display() or "No data",
                        'district': selected_listing.district or "No data",
                        'city': selected_listing.city or "No data",
                        'street': selected_listing.street or "No data",
                        'house_number': selected_listing.house_number or "No data",
                        'apartment_number': selected_listing.apartment_number or "No data",
                        'max_guests': selected_listing.get_max_guests_display() or "No data",
                        'property_type': selected_listing.get_property_type_display() or "No data",
                        'price_per_night': str(selected_listing.price_per_night) if selected_listing.price_per_night is not None
                        else "No data",
                        'discount': str(selected_listing.discount),
                        'rooms': selected_listing.get_rooms_display() or "No data",
                    }
                if self.date_from and self.date_to:
                    snapshot_data['booking_details'] = {'date_from': str(self.date_from),
                                                        'date_to': str(self.date_to),
                                                        'nights': str((self.date_to - self.date_from).days),
                                                        'guests_number': str(self.guests_number)}

                if self.total_price:
                    snapshot_data['total_price'] = str(self.total_price)

                self.snapshot_data = snapshot_data

            self.full_clean(exclude=['snapshot_data'])
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking's Title: {self.listing.title}"

    def __repr__(self):
        return (f"<Booking(user={self.user_id}, date_from={self.date_from}, date_to={self.date_to},"
                f" booking_status={self.booking_status}, guests_number={self.guests_number},"
                f" total_price={self.total_price})>")

    class Meta:
        db_table = 'fma_bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ('-created_at',)
        constraints = [models.CheckConstraint(name='guests_from_1_to_10',
                                              condition=Q(guests_number__gte=1) & Q(guests_number__lte=10),
                                              violation_error_message=_('Guests number must be between 1 and 10!')),
                       models.CheckConstraint(name='end_date_gt_start_date',
                                              condition=Q(date_to__gt=F('date_from')),
                       violation_error_message=_('Booking start date can not be greater than end date!')),
                       models.CheckConstraint(name='booking_total_price_gte_zero',
                                              condition=Q(total_price__gte=0),
                                              violation_error_message=_('Total price can not be less than zero!'))]
        indexes = [models.Index(fields=['-created_at'], name='fma_bookings_created_at_idx'),
                   models.Index(fields=['date_from', 'date_to'], name='fma_bookings_dates_idx'),
                   models.Index(fields=['booking_status'], name='fma_bookings_status_idx'),
                   models.Index(fields=['listing'], name='fma_bookings_listing_id_idx'),
                   models.Index(fields=['user'], name='fma_bookings_user_id_idx')]

