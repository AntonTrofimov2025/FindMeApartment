from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
from apps.core.models import UniqueID, TimeStampedModel, Countries, PropertyType, RoomCount
from django_extensions.db.fields import AutoSlugField
from pytils.translit import slugify
from django.utils import timezone
from managers.listings import ListingSoftDeleteManager



class Listing(UniqueID, TimeStampedModel):

    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)],
                             verbose_name="Listing's Title")
    description = models.TextField(verbose_name="Listing's description")
    user = models.ForeignKey(get_user_model(), related_name='listings', on_delete=models.PROTECT,
                             verbose_name='User', help_text='Current selected user')
    country = models.SmallIntegerField(choices=Countries, default=Countries.GERMANY, help_text='Selected country',
                                       verbose_name='Country')
    city = models.CharField(max_length=50, validators=[MinLengthValidator(3)], help_text='Specified city',
                            verbose_name='City')
    street = models.CharField(max_length=100, validators=[MinLengthValidator(3)], help_text='Specified street',
                              verbose_name='Street')
    house_number = models.CharField(max_length=10, validators=[MinLengthValidator(1)],
                                    help_text='Specified house number', verbose_name='House number')
    active = models.BooleanField(default=True, verbose_name='Available?')
    property_type = models.CharField(max_length=9, choices=PropertyType, default=PropertyType.APARTMENT,
                                     help_text='Selected Property Type', verbose_name='Property type')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Current price')
    rooms = models.SmallIntegerField(choices=RoomCount, default=RoomCount.ONE, verbose_name="Selected room's quantity")

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    objects = ListingSoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Listing's Title: {self.title}"

    def __repr__(self):
        return (f"<Listing(title={self.title}, user={self.user}, country={self.country}, city={self.city},"
                f" street={self.street}, house_number={self.house_number}, active={self.active},"
                f" property_type={self.property_type}, price={self.price}, rooms={self.rooms})>")

