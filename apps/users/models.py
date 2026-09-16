from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from apps.core.models import UniqueID, TimeStampedModel
from django.utils import timezone
from .managers.users import UserSoftDeleteManager, AllUserSoftDeleteManager
from django.utils.translation import gettext_lazy as _
from apps.users.validators import validate_birth_date
import os
from django.db.models import Q
from apps.core.utils import validate_extension, validate_file_size


def get_avatar_upload_path(instance, filename):
    user_id = instance.id if instance.id else 'Unknown'

    return os.path.join('users', str(user_id), 'avatars', filename)


class User(AbstractBaseUser, PermissionsMixin, UniqueID):

    username = models.CharField(blank=True, max_length=50, help_text=_("Specified Username"), verbose_name=_('Username'))
    email = models.EmailField(unique=True, max_length=255, help_text=_("Your email"), verbose_name=_('Email'))
    first_name = models.CharField(max_length=50, blank=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=50, blank=True, verbose_name=_('Last name'))
    birth_date = models.DateField(null=True, blank=True, help_text=_('Your birthday'), verbose_name=_('Birthday'),
                                  validators=[validate_birth_date])
    avatar = models.ImageField(upload_to=get_avatar_upload_path, null=True, blank=True, verbose_name=_('Avatar'),
                validators=[validate_extension, validate_file_size])

    phone = models.CharField(max_length=75, blank=True, default='', help_text=_('Specified phone number'),
                             verbose_name=_('Phone number'))
    last_login = models.DateTimeField(null=True, verbose_name=_('Last login'))

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True, help_text=_('Date of join'), verbose_name=_('Joined at'))
    updated_at = models.DateTimeField(auto_now=True, help_text=_('Date of update'), verbose_name=_('Updated at'))
    deleted_at = models.DateTimeField(null=True, blank=True, help_text=_('Date of deletion'), verbose_name=_('Deleted at'))

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    objects = UserSoftDeleteManager()
    all_objects = AllUserSoftDeleteManager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.is_active = False
        super().save(update_fields=['deleted_at', 'is_active', 'updated_at'])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __repr__(self):
        return (f"<User(username={self.username}, email={self.email}, first_name={self.first_name},"
                f" last_name={self.last_name}, birth_date={self.birth_date}, phone={self.phone},"
                f" is_staff={self.is_staff}, is_active={self.is_active}, date_joined={self.date_joined})>")

    def __str__(self):
        return f"User: {self.username} {self.email}"

    class Meta:
        constraints = [models.UniqueConstraint(
                        fields=['phone'],
                        condition=~Q(phone=''),
                        name='unique_user_phone',
                        violation_error_message=_('A user with this phone number already exists!'))]
        indexes = [
            models.Index(fields=['email'], name='fma_user_email_idx'),
            models.Index(fields=['last_name', 'first_name'], name='fma_user_fullname_idx'),
        ]

