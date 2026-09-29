from rest_framework import serializers
from apps.bookings.models import Booking
from apps.core.models import StatusChoices
from django.utils.translation import gettext_lazy as _


class BookingSerializer(serializers.ModelSerializer):
    """
    Output data representation serializer for established booking records.

    Used to safely serialize detailed reservation payloads. Fully exposes
    pre-calculated total price metrics and immutable deep JSON metadata structures
    extracted from `snapshot_data`.
    """

    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number', 'snapshot_data',
                  'total_price', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'total_price', 'snapshot_data', 'booking_status',
                            'created_at', 'updated_at', 'deleted_at']

    def to_representation(self, instance):
        """
        Dynamically masks precise address vectors inside snapshot_data for Tenants
        if the booking transaction has not been officially confirmed by the host yet.
        """
        to_representation = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None

        is_owner = user and user.is_authenticated and instance.listing.user_id == user.id
        is_staff = user and user.is_authenticated and (user.is_staff or user.is_superuser)

        if not is_owner and not is_staff:
            if instance.booking_status not in [StatusChoices.CONFIRMED, StatusChoices.CHECKED_IN,
                                               StatusChoices.COMPLETED]:
                if ('snapshot_data' in to_representation
                        and to_representation['snapshot_data'] and 'property_data' in to_representation['snapshot_data']):
                    to_representation['snapshot_data']['property_data']['street'] = "Hidden until booking confirmation"
                    to_representation['snapshot_data']['property_data']['house_number'] = "X"
                    to_representation['snapshot_data']['property_data']['apartment_number'] = "X"

        return to_representation

class BookingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Input validation serializer for booking creation and tenancy modifications.

    Defines the exact transactional fields accepted from clients during reservations.
    Keeps status fields and pricing metadata locked as `read_only` to prevent payload forgery.

    Validation Rules:
        - Restricts operational updates strictly to instances currently holding a 'PENDING' status.
          Throws a 400 validation block if users try to modify confirmed or archived trips.
    """

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'user', 'date_from', 'date_to', 'booking_status', 'guests_number',
                  'total_price', 'deleted_at']
        read_only_fields = ['id', 'total_price', 'user', 'booking_status', 'deleted_at']

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

