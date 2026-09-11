from rest_framework import serializers
from apps.reviews.models import Review
from django.core.validators import ValidationError
import copy


class ReviewSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = ['id', 'booking', 'property_rating', 'location_rating', 'text', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'deleted_at', 'created_at', 'updated_at',]

    def validate(self, attrs):
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

