from rest_framework import serializers
from apps.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    overall_rating = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'district', 'city', 'street', 'house_number',
                  'overall_rating', 'apartment_number', 'price_per_night', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'user', 'overall_rating', 'created_at', 'updated_at', 'deleted_at']

