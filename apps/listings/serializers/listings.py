from rest_framework import serializers
from apps.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    overall_rating = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating', 'apartment_number', 'max_guests',
                  'price_per_night', 'final_price_per_night', 'rooms', 'is_active', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'user', 'overall_rating', 'is_active', 'deleted_at', 'final_price_per_night']


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    overall_rating = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'country', 'district', 'city', 'street', 'house_number',
                  'property_type', 'discount', 'overall_rating',
                  'apartment_number', 'max_guests', 'price_per_night', 'rooms', 'is_active', 'deleted_at']
        read_only_fields = ['id', 'user', 'is_active', 'deleted_at']

    # def validate(self, attrs):
    #     if self.instance:
    #         instance = copy.deepcopy(self.instance)
    #         for field, value in attrs.items():
    #             setattr(instance, field, value)
    #     else:
    #         instance = Listing(**attrs)
    #
    #     try:
    #         instance.clean()
    #     except ValidationError as e:
    #         e = e.message_dict if hasattr(e, 'message_dict') else e.messages
    #         raise serializers.ValidationError(e)
    #
    #     return attrs

