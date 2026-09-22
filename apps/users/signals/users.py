from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save



@receiver(post_save, sender=get_user_model(), dispatch_uid='assign_default_user_group')
def assign_group(sender, instance, created, **kwargs):
    """
    Automated identity access management pipeline triggered upon successful user registration.

    Guarantees that every newly created user profile is implicitly bound to the system
    'Tenant' security group, establishing default system-wide permission configurations
    immediately upon database instantiation.
    """
    if created:
        tenant_group, _ = Group.objects.get_or_create(name='Tenant')
        instance.groups.add(tenant_group)

