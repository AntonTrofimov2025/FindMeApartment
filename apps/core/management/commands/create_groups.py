from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Generator
from django.db.models import Q


User = get_user_model()


class Command(BaseCommand):
    """
    Management command to initialize and seed system-wide Role-Based Access Control (RBAC) groups.

    Parses the structured 'ROLE_PERMISSION' mapping schema from project settings,
    automatically handles the atomic lookup or creation of target security groups (e.g., Tenant, Landlord),
    and binds explicit Django auth application permissions to establish deterministic access boundaries.
    """
    help = 'Initializes default security groups and assigns respective permission constraints.'

    @staticmethod
    def add_permission(group, permissions: Generator[str]):
        matched_permissions = Q()
        for permission in permissions:
            app_label, codename = permission.split('.', 1)
            matched_permissions |= Q(content_type__app_label=app_label.lower(), codename=codename.lower())
        try:
            matched_permissions = Permission.objects.filter(matched_permissions)
            if matched_permissions.exists():
                group.permissions.set(matched_permissions)
            else:
                print(f"The requested rights have not been added: (Not found in db.)")
        except (ValueError, Permission.DoesNotExist):
            print(f"The requested rights have not been added.")

    @staticmethod
    def create_permission():
        for group_name, permissions in settings.ROLE_PERMISSION.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permission_gen = (permission for permission in permissions)
            Command.add_permission(group, permission_gen)

    def handle(self, *args, **kwargs):
        self.create_permission()