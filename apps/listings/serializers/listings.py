from rest_framework import serializers
from apps.listings.models import Listing
from .photos import PhotoSerializer


class ListingSerializer(serializers.ModelSerializer):
    """
    Consumer facing data representation serializer for property details.

    Exposes comprehensive read-only property fields including computed aggregates
    such as `overall_rating` and the quantized Decimal `final_price_per_night`.
    """
    overall_rating = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating', 'apartment_number', 'max_guests', 'photos',
                  'price_per_night', 'final_price_per_night', 'rooms', 'is_active', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'user', 'overall_rating', 'is_active', 'deleted_at', 'final_price_per_night']


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Operational schema serializer for publishing or editing property assets.

    Locks critical system ownership fields as `read_only` to guarantee that
    the active authenticated user is automatically bound as the property host.
    """
    overall_rating = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating',
                  'apartment_number', 'max_guests', 'price_per_night', 'rooms', 'is_active', 'deleted_at']
        read_only_fields = ['id', 'user', 'is_active', 'deleted_at']

