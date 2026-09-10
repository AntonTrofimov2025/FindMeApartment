from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from apps.core.models import UniqueID, TimeStampedModel
from django.utils import timezone
from .managers.users import UserSoftDeleteManager
from django.utils.translation import gettext_lazy as _


class User(AbstractBaseUser, PermissionsMixin, UniqueID):

    # class Roles(models.TextChoices):
    #     TENANT = 'tenant', _('Tenant')
    #     LANDLORD = 'landlord', _('Landlord')

    username = models.CharField(blank=True, max_length=50, help_text="Specified Username", verbose_name='Username')
    email = models.EmailField(unique=True, max_length=255, help_text="Your email", verbose_name='Email')
    first_name = models.CharField(max_length=50, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Last name')
    birth_date = models.DateField(null=True, blank=True, help_text='Your birthday', verbose_name='Birthday')
    # Проверку birthday сделай, то что человеку 18 лет
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True, verbose_name='Avatar')

    phone = models.CharField(max_length=75, blank=True, default='', help_text='Specified phone number', verbose_name='Phone number')
    # Проверку тел номера сделай
    last_login = models.DateTimeField(null=True, verbose_name='Last login')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    ##################################################################################
    # role = models.CharField(max_length=15, choices=Roles, default=Roles.TENANT,    #
    #                         help_text='Select your role', verbose_name='Your role')#
    # Нужно переделать через стандартные django группы                               #
    ##################################################################################

    date_joined = models.DateTimeField(auto_now_add=True, help_text='Date of join', verbose_name='Joined at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Date of update', verbose_name='Updated at')
    deleted_at = models.DateTimeField(null=True, help_text='Date of deletion', verbose_name='Deleted at')

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    objects = UserSoftDeleteManager()
    all_objects = UserManager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active', 'updated_at'])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __repr__(self):
        return (f"<User(username={self.username}, email={self.email}, first_name={self.first_name},"
                f" last_name={self.last_name}, birth_date={self.birth_date}, phone={self.phone},"
                f" is_staff={self.is_staff}, is_active={self.is_active}, date_joined={self.date_joined})>")

    def __str__(self):
        return f"User: {self.username} {self.email}"
