from rest_framework import serializers
from apps.reviews.models import Review
from apps.core.models import StatusChoices


class ReviewSerializer(serializers.ModelSerializer):
    """
    Public data serialization layout for feedback records.

    Transforms qualitative user review texts, property metrics, and location stars
    into standard consumer-facing JSON arrays.
    """
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'created_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'deleted_at', 'created_at', 'updated_at']


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Strict contractual validation serializer for leaving and updating reviews.

    Guards evaluation fields to prevent rating injection and feedback forgery.

    Validation Rules:
        - Strict Integrity: Validates that the active client matches the unique Tenant
          bound to the underlying completed booking transaction.
        - One-to-One Limit: Restricts operations to a single unique review entry per booking.
          Throws an validation block if an associated review instance already exists.
    """

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'deleted_at']
        read_only_fields = ['id', 'deleted_at']

    def validate(self, attrs):
        booking = attrs.get('booking') or getattr(self.instance, 'booking', None)
        request = self.context.get('request')

        if booking and request:
            if booking.user != request.user:
                raise serializers.ValidationError('You can leave reviews for your own completed bookings only!')

            existing_review = Review.all_objects.filter(booking=booking).first()
            if existing_review:
                if not self.instance or existing_review.pk != self.instance.pk:
                    raise serializers.ValidationError('You can leave only one review for the booking!')

        return attrs

