from django_filters import rest_framework as filters
from apps.listings.models import Listing


class ListingFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='lte')

    class Meta:
        model = Listing
        fields = ['city', 'district', 'property_type']

