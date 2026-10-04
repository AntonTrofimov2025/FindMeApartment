from django.contrib import admin
from apps.listings.models import Listing, Photo
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.utils import timezone


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'user', 'get_photo', 'booking_count', 'property_type', 'short_description',
        'country', 'city', 'district', 'street', 'house_number', 'apartment_number',
        'is_active', 'price_per_night', 'max_guests', 'discount', 'rooms', 'show_is_deleted'
    )
    readonly_fields = ('deleted_at',)
    search_fields = ('title', 'city', 'country', 'user__email')
    list_filter = ('property_type', 'country', 'created_at')
    ordering = ('-created_at',)

    @admin.display(boolean=True, description=_('Deleted?'))
    def show_is_deleted(self, listing):
        return listing.is_deleted

    @admin.display(description=_('Main Photo'))
    def get_photo(self, listing):
        if listing.photos.first() and listing.photos.first().photo:
            return mark_safe(f'<img src="{listing.photos.first().photo.url}" style="max-height: 50px; max-width:'
                             f' 70px; border-radius: 6px; object-fit: cover;" />')
        return mark_safe('<span style="color: #999; font-style: italic;">- No photo -</span>')

    @admin.display(description=_("Number of bookings"))
    def booking_count(self, obj):
        return obj._booking_count

    @admin.display(description=_('Description'))
    def short_description(self, obj):
        if obj.description and len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description

    def get_queryset(self, request):
        return super().get_queryset(request).model.all_objects.get_queryset().select_related(
            'user').prefetch_related('photos').annotate(_booking_count=Count('bookings'))

    @admin.action(description="Restore selected deleted listings")
    def restore_listings(self, request, queryset):
        listings = queryset.update(deleted_at=None, is_active=True)
        self.message_user(request, f"Successfully restored {listings} listings. 🎉")

    @admin.action(description="Soft delete selected listings")
    def soft_delete_listings(self, request, queryset):
        listings = queryset.update(deleted_at=timezone.now(), is_active=False)
        self.message_user(request, f"Successfully soft deleted {listings} listings.")

    actions = [restore_listings, soft_delete_listings]



@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_listing_title', 'get_mini_photo', 'get_listing_email',
        'photo_number', 'created_at', 'show_is_deleted'
    )
    readonly_fields = ('deleted_at',)

    search_fields = (
        'listing__title', 'listing__city', 'listing__user__email'
    )

    list_filter = ('photo_number', 'created_at')
    ordering = ('-created_at',)

    @admin.display(description=_('Listing Title'))
    def get_listing_title(self, obj):
        return obj.listing.title

    @admin.display(description=_('Landlord Email'))
    def get_listing_email(self, obj):
        return obj.listing.user.email

    @admin.display(boolean=True, description=_('Deleted?'))
    def show_is_deleted(self, photo):
        return photo.is_deleted

    @admin.display(description=_('Photo Preview'))
    def get_mini_photo(self, obj):
        if obj.photo:
            return mark_safe(
                f'<img src="{obj.photo.url}" '
                f'style="max-height: 50px; max-width: 70px; border-radius: 6px; object-fit: cover;" />'
            )
        return mark_safe('<span style="color: #999; font-style: italic;">- No image -</span>')

    def get_queryset(self, request):
        return super().get_queryset(request).model.all_objects.select_related('listing__user')

    @admin.action(description="Restore selected deleted photos")
    def restore_photos(self, request, queryset):
        photos = queryset.update(deleted_at=None)
        self.message_user(request, f"Successfully restored {photos} photos. 🎉")

    @admin.action(description="Soft delete selected photos")
    def soft_delete_photos(self, request, queryset):
        photos = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"Successfully soft deleted {photos} photos.")

    actions = [restore_photos, soft_delete_photos]