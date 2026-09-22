from rest_framework import serializers
from apps.listings.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """
    Multipart parsing asset validation serializer for property media attachments.

    Maps structural binary file payloads to designated asset foreign key relations.
    Protects administrative historical records by locking modification dates as read-only.
    """
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = ['id', 'listing', 'photo', 'photo_number', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'is_deleted', 'deleted_at']

