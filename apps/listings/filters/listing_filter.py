from django_filters import rest_framework as filters
from apps.listings.models import Listing
from apps.core.models import Countries, RoomCount, MaxGuests
from django.db.models import F, ExpressionWrapper, DecimalField


class ListingFilter(filters.FilterSet):
    """
    Advanced multi-attribute catalog search criteria mapper.

    Binds frontend query parameters (e.g., price ranges, localized text metrics,
    and strict choice enumerations) to matching transactional properties
    in the database to facilitate precise catalog filtering.

    Enforces dynamic discount-aware price calculations and capacity matching.
    """
    min_price = filters.NumberFilter(method='filter_min_price')
    max_price = filters.NumberFilter(method='filter_max_price')
    min_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    city = filters.CharFilter(field_name='city', lookup_expr='istartswith')
    country = filters.ChoiceFilter(field_name='country', lookup_expr='exact', choices=Countries.choices)
    rooms = filters.ChoiceFilter(field_name='rooms', lookup_expr='exact',
                                 choices=RoomCount.choices)
    guests = filters.ChoiceFilter(field_name='max_guests', lookup_expr='gte', choices=MaxGuests.choices,
                                  help_text='Select minimal guests quantity')

    class Meta:
        model = Listing
        fields = ['district', 'property_type']

    def filter_min_price(self, queryset, name, value):
        """
        Filters properties where the dynamically calculated final price
        (base price * discount coefficient) is greater than or equal to the target value.
        """
        return queryset.annotate(final_price=ExpressionWrapper(F('price_per_night') * F('discount'),
                                                        output_field=DecimalField())).filter(final_price__gte=value)

    def filter_max_price(self, queryset, name, value):
        """
        Filters properties where the dynamically calculated final price
        (base price * discount coefficient) is less than or equal to the target value.
        """
        return queryset.annotate(final_price=ExpressionWrapper(F('price_per_night') * F('discount'),
                                                        output_field=DecimalField())).filter(final_price__lte=value)
