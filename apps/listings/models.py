from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator
from apps.core.models import UniqueID, TimeStampedModel, Countries, PropertyType, RoomCount, MaxGuests
from django_extensions.db.fields import AutoSlugField
from pytils.translit import slugify
from django.utils import timezone
from managers.listings import ListingsSoftDeleteManager



class Listing(UniqueID, TimeStampedModel):

    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)],
                             verbose_name="Listing's Title")
    description = models.TextField(verbose_name="Listing's description")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='listings', on_delete=models.PROTECT,
                             verbose_name='User', help_text='Current selected user')
    country = models.SmallIntegerField(choices=Countries, default=Countries.GERMANY, help_text='Selected country',
                                       verbose_name='Country')
    district = models.CharField(max_length=50, validators=[MinLengthValidator(3)], help_text='Specified district',
                            verbose_name='District')
    city = models.CharField(max_length=50, validators=[MinLengthValidator(3)], help_text='Specified city',
                            verbose_name='City')
    street = models.CharField(max_length=100, validators=[MinLengthValidator(3)], help_text='Specified street',
                              verbose_name='Street')
    house_number = models.CharField(max_length=10, validators=[MinLengthValidator(1)],
                                    help_text='Specified house number', verbose_name='House number')
    apartment_number = models.CharField(max_length=10, validators=[MinLengthValidator(1)], null=True, blank=True,
                                        help_text='Specified apartment number', verbose_name='Apartment number')
    is_active = models.BooleanField(default=True, verbose_name='Available?')
    max_guests = models.SmallIntegerField(choices=MaxGuests, default=MaxGuests.TWO,
                                          help_text='Selected guests max quantity', verbose_name='Max guests')
    property_type = models.CharField(max_length=15, choices=PropertyType, default=PropertyType.APARTMENT,
                                     help_text='Selected Property Type', verbose_name='Property type')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Current price')
    rooms = models.SmallIntegerField(choices=RoomCount, default=RoomCount.ONE, help_text="Selected room's quantity",
                                     verbose_name='Rooms')

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    objects = ListingsSoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Listing's Title: {self.title}"

    def __repr__(self):
        return (f"<Listing(title={self.title}, user={self.user}, country={self.country}, city={self.city},"
                f" street={self.street}, house_number={self.house_number}, apartment_number={self.apartment_number},"
                f" is_active={self.is_active},"
                f" property_type={self.property_type}, price={self.price}, rooms={self.rooms})>")

    class Meta:
        db_table = 'fma_listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        constraints = [models.UniqueConstraint(fields=['user', 'country', 'city', 'district', 'street',
                                                       'house_number', 'apartment_number'],
                                               name='unique_user_address',
                                               violation_error_message='Such an address combination already exists!')]
        indexes = [models.Index(fields=['is_active'], name='fma_listings_is_active_idx'),
                   models.Index(fields=['is_active', 'city'], name='fma_listings_is_active_city_idx'),
                   models.Index(fields=['is_active', 'price'], name='fma_listings_is_active_price_idx'),
                   models.Index(fields=['city'], name='fma_listings_city_idx'),
                   models.Index(fields=['price'], name='fma_listings_price_idx'),
                   models.Index(fields=['rooms'], name='fma_listings_rooms_idx')]


# Когда буду делать модель отзывов то надо учесть момент с OneToOne field (booking к review),
# то есть учесть нюанс чтобы при удалении букинга не удалялся отзыв, это плохо.
# Обратная ситуация: удаляем отзыв - удаляется объявление, отличная ситуация :
