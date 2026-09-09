from django.contrib.auth.models import UserManager
from django.db import models
from django.utils import timezone


class UserSoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now(), is_active=False)


class UserSoftDeleteManager(UserManager):
    def get_queryset(self):
        # return super().get_queryset().filter(deleted_at__isnull=True)
        return UserSoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

