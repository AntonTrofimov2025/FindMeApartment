from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.bookings.models import Booking
from apps.core.models import StatusChoices


@receiver(post_save, sender=Booking, dispatch_uid="send_booking_status_email")
def send_booking_email_on_status_change(sender, instance, created, **kwargs):
    tenant_name = instance.user.first_name or "Tenant"
    landlord_name = instance.listing.user.first_name or "Landlord"
    landlord_email = instance.listing.user.email
    tenant_email = instance.user.email
    listing_title = instance.listing.title

    # if created:
    #     subject = "New Booking Request for your listing!"
    #     message = f"Hello, {landlord_name}!\n\n" \
    #               f"User {tenant_name} has sent a booking request for your property '{listing_title}' " \
    #               f"from {instance.date_from} to {instance.date_to}.\n" \
    #               f"Please log in to your account to approve or reject this request."
    #
    #     send_mail(subject, message, None, [landlord_email], fail_silently=True)
    #     return

    if created:
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

    updated_fields = kwargs.get('updated_fields')
    if updated_fields and 'booking_status' not in updated_fields:
        return

    # if instance.booking_status == StatusChoices.CONFIRMED:
    #     subject = "Your booking has been CONFIRMED! 🎉"
    #     message = f"Great news, {tenant_name}!\n\n" \
    #               f"Your booking for '{listing_title}' from {instance.date_from} to {instance.date_to} " \
    #               f"has been successfully confirmed by the landlord.\n" \
    #               f"Total price: {instance.total_price} €. Enjoy your stay!"
    #     send_mail(subject, message, None, [tenant_email], fail_silently=True)

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


    # elif instance.booking_status == StatusChoices.REJECTED:
    #     subject = "Update on your booking request"
    #     message = f"Hello, {tenant_name}.\n\n" \
    #               f"Unfortunately, your booking request for '{listing_title}' " \
    #               f"was rejected by the landlord. No funds were charged."
    #     send_mail(subject, message, None, [tenant_email], fail_silently=True)

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


    # elif instance.booking_status == StatusChoices.CANCELLED:
    #     subject = "Booking cancelled"
    #     message = f"Hello, {landlord_name}.\n\n" \
    #               f"The booking for your property '{listing_title}' " \
    #               f"from {instance.date_from} to {instance.date_to} has been cancelled.\n" \
    #               f"We are very sorry for this inconvenience."
    #     send_mail(subject, message, None, [landlord_email], fail_silently=True)
    #

    elif instance.booking_status == StatusChoices.CANCELLED:
        subject = "Booking cancelled"

        context = {
            'landlord_name': landlord_name,
            'listing_title': listing_title,
            'date_from': instance.date_from,
            'date_to': instance.date_to,
        }

        html_message = render_to_string('email_booking_cancelled.html', context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[landlord_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)

