from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save



# @receiver(user_logged_in, dispatch_uid="update_user_last_login_on_login")
# def logged_id(sender, request, user, **kwargs):
#     if user.last_login is None:
#         user.last_login = timezone.now()
#         user.save(update_fields=['last_login'])

@receiver(post_save, sender=get_user_model(), dispatch_uid='assign_default_user_group')
def assign_group(sender, instance, created, **kwargs):
    if created:
        tenant_group, _ = Group.objects.get_or_create(name='Tenant')
        instance.groups.add(tenant_group)

