from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from config.settings import ROLE_PERMISSION
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):

    @staticmethod
    def add_permission(group, permissions: list[tuple[str, str]] | tuple[str, str]):
        if isinstance(permissions, tuple):
            permissions = [permissions]
        for app_label, codename in permissions:
            try:
                matched_permissions = Permission.objects.filter(content_type__app_label=app_label.lower(),
                                                                codename=codename.lower())
                if matched_permissions.exists():
                    group.permissions.add(*matched_permissions)
                else:
                    print(f"The requested right has not been added: {app_label}.{codename} (Not found in db.)")
            except (ValueError, Permission.DoesNotExist):
                print(f"The requested right has not been added: {app_label}.{codename}")

    @staticmethod
    def create_permission():
        for key, value in ROLE_PERMISSION.items():
            group, _ = Group.objects.get_or_create(name=key)
            permission_list = [tuple(permission.split('.', 1)) for permission in value]
            Command.add_permission(group, permission_list)

    def handle(self, *args, **kwargs):
        self.create_permission()