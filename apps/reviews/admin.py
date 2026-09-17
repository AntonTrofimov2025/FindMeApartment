from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_property_stars', 'get_location_stars', 'get_tenant_email',
        'get_listing_title', 'short_text', 'created_at', 'show_is_deleted'
    )
    readonly_fields = ('deleted_at',)

    search_fields = (
        'id', 'text', 'booking__user__email', 'booking__listing__title'
    )

    list_filter = ('property_rating', 'location_rating', 'created_at')

    ordering = ('-created_at',)

    @admin.display(description=_('Prop Rating'))
    def get_property_stars(self, obj):
        stars = int(obj.property_rating) if obj.property_rating else 0
        return mark_safe(f'<span style="color: #ffb400;">{"★" * stars}{"☆" * (5 - stars)}</span>')

    @admin.display(description=_('Loc Rating'))
    def get_location_stars(self, obj):
        stars = int(obj.location_rating) if obj.location_rating else 0
        return mark_safe(f'<span style="color: #00a699;">{"★" * stars}{"☆" * (5 - stars)}</span>')

    @admin.display(description=_('Tenant'))
    def get_tenant_email(self, obj):
        return obj.booking.user.email

    @admin.display(description=_('Listing'))
    def get_listing_title(self, obj):
        return obj.booking.listing.title

    @admin.display(description=_('Review Text'))
    def short_text(self, obj):
        if obj.text and len(obj.text) > 80:
            return f"{obj.text[:80]}..."
        return obj.text or _("- No text -")

    @admin.display(boolean=True, description=_('Deleted?'))
    def show_is_deleted(self, review):
        return review.is_deleted

    def get_queryset(self, request):
        return Review.all_objects.get_queryset().select_related('booking__user', 'booking__listing')
