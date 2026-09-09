from rest_framework import serializers
from apps.bookings.models import Booking
from django.core.exceptions import ValidationError


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, attrs):
        instance = Booking(**attrs)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

