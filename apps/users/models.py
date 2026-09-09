from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from apps.core.models import UniqueID, TimeStampedModel


class User(AbstractBaseUser, PermissionsMixin, UniqueID, TimeStampedModel):

    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)

    phone = models.CharField(max_length=75, blank=True, default='')
    last_login = models.DateTimeField(null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)