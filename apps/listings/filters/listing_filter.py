from django_filters import rest_framework as filters
from apps.listings.models import Listing


class ListingFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    min_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    city = filters.CharFilter(field_name='city', lookup_expr='exact')
    country = filters.ChoiceFilter(field_name='country', lookup_expr='exact')
    rooms = filters.ChoiceFilter(field_name='rooms', lookup_expr='exact')

    class Meta:
        model = Listing
        fields = ['district', 'property_type']

