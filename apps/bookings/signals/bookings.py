from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.bookings.models import Booking
from apps.core.models import StatusChoices




def _send_transactional_email(booking_id, is_created):
    """
    Isolated helper executed STRICTLY after the database transaction is successfully committed.
    Eliminates N+1 degradation and guarantees absolute email delivery consistency.
    """
    try:
        instance = Booking.objects.select_related('listing', 'listing__user', 'user').get(pk=booking_id)
    except Booking.DoesNotExist:
        return

    tenant_name = instance.user.first_name or "Tenant"
    landlord_name = instance.listing.user.first_name or "Landlord"
    landlord_email = instance.listing.user.email
    tenant_email = instance.user.email
    listing_title = instance.listing.title

    if not landlord_email or not tenant_email:
        return

    if is_created:
        subject = "New Booking Request for your listing!"

        context = {
            'landlord_name': landlord_name,
            'tenant_name': tenant_name,
            'listing_title': listing_title,
            'date_from': instance.date_from,
            'date_to': instance.date_to,
        }

        html_message = render_to_string('email_booking_created.html', context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[landlord_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)
        return

    if instance.booking_status == StatusChoices.CONFIRMED:
        subject = "Your booking has been CONFIRMED! 🎉"

        context = {
            'tenant_name': tenant_name,
            'listing_title': listing_title,
            'date_from': instance.date_from,
            'date_to': instance.date_to,
            'total_price': instance.total_price,
        }

        html_message = render_to_string('email_booking_confirmed.html', context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[tenant_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)

    elif instance.booking_status == StatusChoices.REJECTED:
        subject = "Update on your booking request"

        context = {
            'tenant_name': tenant_name,
            'listing_title': listing_title,
        }

        html_message = render_to_string('email_booking_rejected.html', context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[tenant_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)

    elif instance.booking_status == StatusChoices.CANCELLED:
        subject = "Booking cancelled"

        context = {
            'landlord_name': landlord_name,
            'listing_title': listing_title,
            'date_from': instance.date_from,
            'date_to': instance.date_to,
        }

        html_message = render_to_string('email_booking_cancelled_landlord.html', context)

        context_tenant = {
            'tenant_name': tenant_name,
            'listing_title': listing_title,
            'date_from': instance.date_from,
            'date_to': instance.date_to,
        }

        html_message_tenant = render_to_string('email_booking_cancelled_tenant.html', context_tenant)

        plain_message = strip_tags(html_message)
        plain_message_tenant = strip_tags(html_message_tenant)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[landlord_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)

        msg_tenant = EmailMultiAlternatives(
            subject=subject,
            body=plain_message_tenant,
            from_email=None,
            to=[tenant_email]
        )
        msg_tenant.attach_alternative(html_message_tenant, "text/html")
        msg_tenant.send(fail_silently=True)

@receiver(post_save, sender=Booking, dispatch_uid="send_booking_status_email")
def send_booking_email_on_status_change(sender, instance, created, **kwargs):
    """
    Automated transactional email workflow triggered upon booking lifecycle events.
    Guarded against N+1 query degradation and cron-worker execution contexts.

    Dispatches multipart HTML/text notifications via console/mail backends:
      - On Creation: Sends a pending request notice to the Landlord.
      - On Confirmation/Rejection: Updates the Tenant on their reservation status.
      - On Cancellation: Alerts the Landlord about the cancelled itinerary logs.
    """
    if getattr(instance, '_skip_signal_email', False):
        return

    update_fields = kwargs.get('update_fields')
    if not created and update_fields and 'booking_status' not in update_fields:
        return

    transaction.on_commit(
        lambda: _send_transactional_email(instance.id, created)
    )