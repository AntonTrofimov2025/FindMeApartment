from rest_framework import serializers
from apps.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Listing
        fields = ['id', 'title', 'user', 'description', 'district', 'city', 'street', 'house_number',
                  'apartment_number', 'price']
        read_only_fields = ['id', 'user']

