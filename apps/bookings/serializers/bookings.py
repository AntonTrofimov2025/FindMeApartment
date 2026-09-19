from rest_framework import serializers
from apps.bookings.models import Booking
from apps.core.models import StatusChoices
from django.utils.translation import gettext_lazy as _


class BookingSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number', 'snapshot_data',
                  'total_price', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'total_price', 'snapshot_data', 'booking_status',
                            'created_at', 'updated_at', 'deleted_at']


class BookingCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number', 'snapshot_data',
                  'total_price', 'deleted_at']
        read_only_fields = ['id', 'total_price', 'user', 'booking_status', 'snapshot_data', 'deleted_at']

    def validate(self, attrs):
        if self.instance:
            if self.instance.booking_status != StatusChoices.PENDING:
                raise serializers.ValidationError(_("You can only modify bookings that are in 'Pending' status!"))
        #     instance = copy.deepcopy(self.instance)
        #     for field, value in attrs.items():
        #         setattr(instance, field, value)
        # else:
        #     instance = Booking(**attrs)
        #     if 'request' in self.context:
        #         instance.user = self.context['request'].user

        # try:
        #     instance.clean()
        # except ValidationError as e:
        #     e = e.message_dict if hasattr(e, 'message_dict') else e.messages
        #     raise serializers.ValidationError(e)

        return attrs

