from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import UniqueID, TimeStampedModel, Countries, PropertyType, RoomCount, MaxGuests
from django_extensions.db.fields import AutoSlugField
from pytils.translit import slugify
from django.utils import timezone
from .managers.listings import ListingsSoftDeleteManager
from .managers.photo_manager import PhotoSoftDeleteManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Q
from django.db.models.functions import Round
import os
from decimal import Decimal
from apps.core.utils import validate_extension, validate_file_size



class Listing(UniqueID, TimeStampedModel):

    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)],
                             verbose_name=_("Listing's Title"))
    description = models.TextField(verbose_name=_("Listing's description"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='listings', on_delete=models.PROTECT,
                             verbose_name=_('User'), help_text='Current selected user')
    country = models.SmallIntegerField(choices=Countries, default=Countries.GERMANY, help_text='Selected country',
                                       verbose_name=_('Country'))
    district = models.CharField(max_length=50, validators=[MinLengthValidator(3)], help_text='Specified district',
                            verbose_name=_('District'))
    city = models.CharField(max_length=50, validators=[MinLengthValidator(3)], help_text='Specified city',
                            verbose_name=_('City'))
    street = models.CharField(max_length=100, validators=[MinLengthValidator(3)], help_text='Specified street',
                              verbose_name='Street')
    house_number = models.CharField(max_length=10, validators=[MinLengthValidator(1)],
                                    help_text='Specified house number', verbose_name=_('House number'))
    apartment_number = models.CharField(max_length=10, validators=[MinLengthValidator(1)], null=True, blank=True,
                                        help_text='Specified apartment number', verbose_name=_('Apartment number'))
    is_active = models.BooleanField(default=True, verbose_name=_('Available?'))
    max_guests = models.SmallIntegerField(choices=MaxGuests, default=MaxGuests.TWO,
                                          help_text='Selected guests max quantity', verbose_name=_('Max guests'))
    property_type = models.CharField(max_length=15, choices=PropertyType, default=PropertyType.APARTMENT,
                                     help_text='Selected Property Type', verbose_name=_('Property type'))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Current price per night'),
                                          validators=[MinValueValidator(Decimal('0.00'))])
    discount = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal("0.01")),
                                                                MaxValueValidator(Decimal("1"))], default=Decimal("1"),
                                   help_text=_('Discount coefficient for price per night'), verbose_name=_('Discount'))
    rooms = models.SmallIntegerField(choices=RoomCount, default=RoomCount.ONE, help_text="Selected room's quantity",
                                     verbose_name=_('Rooms'))

    @property
    def final_price_per_night(self):
        if self.discount < Decimal("1"):
            return (self.price_per_night * self.discount).quantize(Decimal("0.01"))
        return self.price_per_night

    @property
    def overall_rating(self):
        overall_rating = self.bookings.aggregate(
            avg_rating=Round(Avg('review__property_rating'), 2))['avg_rating']
        return overall_rating or 0.0

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        super().save(update_fields=['deleted_at', 'updated_at'])

    objects = ListingsSoftDeleteManager()
    all_objects = models.Manager()

    def clean(self):
        super().clean()
        if self.property_type and self.property_type in [PropertyType.ROOM, PropertyType.APARTMENT] and not self.apartment_number:
            raise ValidationError(_('The apartment number is required for room/apartment property type'))
        if self.property_type and self.property_type in [PropertyType.HOUSE, PropertyType.STUDIO] and self.apartment_number:
            raise ValidationError(_('The house/studio property type can not have an apartment number.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Listing's Title: {self.title}"

    def __repr__(self):
        return (f"<Listing(title={self.title}, user={self.user}, country={self.country}, city={self.city},"
                f" street={self.street}, house_number={self.house_number}, apartment_number={self.apartment_number},"
                f" is_active={self.is_active},"
                f" property_type={self.property_type}, price_per_night={self.price_per_night}, rooms={self.rooms})>")

    class Meta:
        db_table = 'fma_listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ('-created_at',)
        constraints = [models.UniqueConstraint(fields=['user', 'country', 'city', 'district', 'street',
                                                       'house_number', 'apartment_number'],
                                               name='unique_user_address',
                                               violation_error_message=_('Such an address combination already exists!')),
                       models.CheckConstraint(name='discount_from_0.01_to_1',
                                              condition=Q(discount__gt=Decimal("0")) & Q(discount__lte=Decimal("1")),
                                              violation_error_message='Discount is only allowed in range of (0.01 and 1.00).')]
        indexes = [models.Index(fields=['city', 'price_per_night'], name='fma_listings_city_price_idx'),
                   models.Index(fields=['city', 'rooms'], name='fma_listings_city_rooms_idx'),
                   models.Index(fields=['city', 'price_per_night', 'rooms'], name='fma_list_city_price_rooms_idx'),
                   models.Index(fields=['city'], name='fma_listings_city_idx'),
                   models.Index(fields=['price_per_night'], name='fma_listings_price_idx'),
                   models.Index(fields=['rooms'], name='fma_listings_rooms_idx'),
                   models.Index(fields=['district'], name='fma_listings_district_idx'),
                   models.Index(fields=['street'], name='fma_listings_street_idx'),
                   models.Index(fields=['country'], name='fma_listings_country_idx'),
                   models.Index(fields=['title'], name='fma_listings_title_idx'),
                   models.Index(fields=['description'], name='fma_listings_description_idx')]

def get_upload_path(instance, filename):
    listing_id = instance.listing.id if instance.listing_id else 'Unknown'

    return os.path.join('listings', str(listing_id), filename)

class Photo(UniqueID, TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='photos', verbose_name=_('Listing'))
    photo = models.ImageField(upload_to=get_upload_path, verbose_name=_('Photo'),
    validators=[validate_extension, validate_file_size])
    photo_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)],
                                              help_text="Specified photo number", verbose_name=_('Photo number'))


    objects = PhotoSoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        super().save(update_fields=['deleted_at', 'updated_at'])

    class Meta:
        db_table = 'fma_photos'
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ('-created_at',)
        constraints = [models.UniqueConstraint(fields=['listing', 'photo_number'],
                                name='unique_listing_photo_number',
                                violation_error_message=_('Photo with this number already exists for this listing!')
                            )
                        ]
        indexes = [
            models.Index(fields=['listing'], name='fma_listing_idx')
        ]

    def __repr__(self):
        return f"<Photo(listing={self.listing}, photo={self.photo}, photo_number={self.photo_number})>"

    def __str__(self):
        return f"Photo {self.photo.name if self.photo else 'No photo'}"

