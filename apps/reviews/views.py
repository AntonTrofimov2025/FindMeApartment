from rest_framework import viewsets
from .models import Review
from .serializers.reviews import ReviewSerializer, ReviewCreateUpdateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter


class ReviewViewSet(viewsets.ModelViewSet):

    queryset = Review.objects.select_related('booking', 'booking__user', 'booking__listing').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = [
        'property_rating', 'location_rating', 'text', 'booking__user__first_name',
        'booking__user__last_name', 'booking__user__email'
    ]
    filterset_fields = {
        'property_rating': ['exact', 'gte', 'lte'],
        'location_rating': ['exact', 'gte', 'lte'],
        'booking__listing': ['exact']
    }
    ordering_fields = [
        'property_rating', 'location_rating', 'created_at'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateUpdateSerializer
        return ReviewSerializer

