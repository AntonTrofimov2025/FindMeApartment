from rest_framework import serializers
from apps.listings.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = ['id', 'listing', 'photo', 'photo_number', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

