from django.contrib import admin
from apps.bookings.models import Booking
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin


@admin.register(Booking)
class BookingAdmin(SimpleHistoryAdmin):
    list_display = (
        'id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number',
        'total_price', 'created_at', 'updated_at', 'show_is_deleted'
    )
    readonly_fields = ('deleted_at', "snapshot_data", "total_price")
    search_fields = ('id', 'listing__title', 'listing__city', 'listing__country', 'user__email')
    list_filter = ('booking_status', 'date_from', 'date_to')
    ordering = ('-created_at',)
    history_list_display = ('date_from', 'date_to', 'booking_status', 'guests_number', 'total_price')

    @admin.display(boolean=True, description=_('Deleted?'))
    def show_is_deleted(self, booking):
        return booking.is_deleted

    def get_queryset(self, request):
        return Booking.all_objects.get_queryset().select_related('listing', 'user')

