from rest_framework import serializers
from apps.listings.models import Listing
import copy
from django.core.exceptions import ValidationError
from decimal import Decimal


class ListingSerializer(serializers.ModelSerializer):
    overall_rating = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'district', 'city', 'street', 'house_number', 'discount',
                  'overall_rating', 'apartment_number', 'price_per_night', 'final_price_per_night', 'is_deleted',
                  'deleted_at']
        read_only_fields = ['id', 'user', 'overall_rating', 'created_at', 'updated_at', 'deleted_at', 'final_price_per_night']

    def validate(self, attrs):
        if self.instance:
            instance = copy.deepcopy(self.instance)
            for field, value in attrs.items():
                setattr(instance, field, value)
        else:
            instance = Listing(**attrs)

        try:
            instance.clean()
        except ValidationError as e:
            e = e.message_dict if hasattr(e, 'message_dict') else e.messages
            raise serializers.ValidationError(e)

        return attrs

