from rest_framework import serializers
from apps.reviews.models import Review
from django.core.validators import ValidationError
import copy
from apps.core.models import StatusChoices


class ReviewSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'created_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'deleted_at', 'created_at', 'updated_at']


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'deleted_at']
        read_only_fields = ['id', 'deleted_at']

    def validate(self, attrs):
        booking = attrs.get('booking') or (self.instance.booking if self.instance else None)
        request = self.context.get('request')

        if booking and request:
            if booking.user != request.user:
                raise serializers.ValidationError('You can leave reviews for your own completed bookings only!')

            if booking.booking_status != StatusChoices.COMPLETED:
                raise serializers.ValidationError("You can leave review for your booking after it's completed only!")

            if hasattr(booking, 'review'):
                if not self.instance or booking.review.pk != self.instance.pk:
                    raise serializers.ValidationError('You can leave only one review for the booking!')

        if self.instance:
            instance = copy.deepcopy(self.instance)
            for field, value in attrs.items():
                setattr(instance, field, value)
        else:
            instance = Review(**attrs)

        try:
            instance.clean()
        except ValidationError as e:
            e = e.message_dict if hasattr(e, 'message_dict') else e.messages
            raise serializers.ValidationError(e)

        return attrs

