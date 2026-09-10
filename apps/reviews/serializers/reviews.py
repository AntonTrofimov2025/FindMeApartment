from rest_framework import serializers
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'deleted_at', 'created_at', 'updated_at',]

