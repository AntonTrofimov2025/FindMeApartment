from rest_framework import serializers
from apps.listings.models import Listing
from .photos import PhotoSerializer
from apps.bookings.models import Booking, StatusChoices


class ListingSerializer(serializers.ModelSerializer):
    """
    Consumer facing data representation serializer for property details.

    Exposes comprehensive read-only property fields including computed aggregates
    such as `overall_rating` and the quantized Decimal `final_price_per_night`.
    """
    overall_rating = serializers.FloatField(read_only=True)
    final_price_per_night = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating', 'apartment_number', 'max_guests', 'photos',
                  'price_per_night', 'final_price_per_night', 'rooms', 'is_active', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'user', 'overall_rating', 'is_active', 'deleted_at', 'final_price_per_night']
        
    def to_representation(self, instance):
        """
        Dynamically filters out precise address localization vectors to prevent
        unauthorized off-platform disintermediation and protect host privacy.
        """
        to_representation = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None

        is_owner = user and user.is_authenticated and instance.user_id == user.id
        is_staff = user and user.is_authenticated and (user.is_staff or user.is_superuser)

        if not is_owner and not is_staff:

            has_confirmed_booking = getattr(instance, 'has_confirmed_booking', False)

            if not has_confirmed_booking:
                to_representation['street'] = "Hidden until booking confirmation"
                to_representation['house_number'] = "X"
                to_representation['apartment_number'] = "X"

        return to_representation


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Operational schema serializer for publishing or editing property assets.

    Locks critical system ownership fields as `read_only` to guarantee that
    the active authenticated user is automatically bound as the property host.
    """
    overall_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating',
                  'apartment_number', 'max_guests', 'price_per_night', 'rooms', 'is_active', 'deleted_at']
        read_only_fields = ['id', 'user', 'is_active', 'deleted_at']

