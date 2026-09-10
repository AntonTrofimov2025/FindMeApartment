from rest_framework import serializers
from apps.bookings.models import Booking
from django.core.exceptions import ValidationError


class BookingSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number', 'snapshot_data',
                  'total_price', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'total_price', 'snapshot_data', 'booking_status',
                            'created_at', 'updated_at', 'deleted_at']

    def validate(self, attrs):
        if self.instance:
            instance = self.instance
            for field, value in attrs.items():
                setattr(instance, field, value)
        else:
            instance = Booking(**attrs)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

