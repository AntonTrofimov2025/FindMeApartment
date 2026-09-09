from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in, dispatch_uid="update_user_last_login_on_login")
def logged_id(sender, request, user, **kwargs):
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

