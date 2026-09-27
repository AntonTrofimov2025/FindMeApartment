from django.core.management.base import BaseCommand
from apps.bookings.models import Booking
from apps.core.models import StatusChoices
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    """
        Management command to close expired bookings safely.
        Processes updates via explicit .save() chains to guarantee simple_history triggers.
        """
    help = 'Scans for expired CONFIRMED/CHECKED_IN reservations and transitions them to COMPLETED.'

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Scanning database for expired rental contracts...")
        with transaction.atomic():
            expired_bookings = list(Booking.objects.select_for_update().filter(date_to__lt=timezone.localdate(),
                                   booking_status__in=[StatusChoices.CONFIRMED, StatusChoices.CHECKED_IN,
                                                       StatusChoices.PENDING]))

            if not expired_bookings:
                self.stdout.write(self.style.SUCCESS("✨ No expired bookings found. Database is synchronized."))
                return

            success_count = 0

            for booking in expired_bookings:
                try:
                    if booking.booking_status == StatusChoices.PENDING:
                        booking.booking_status = StatusChoices.CANCELLED
                    else:
                        booking.booking_status = StatusChoices.COMPLETED
                    booking._skip_signal_email = True
                    booking.save(update_fields=['booking_status', 'updated_at'])
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to close booking {booking.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"🚀 Done! Successfully finalized {success_count} bookings."))
