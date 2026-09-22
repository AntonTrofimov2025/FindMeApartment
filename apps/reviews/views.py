from rest_framework import viewsets
from .models import Review
from .serializers.reviews import ReviewSerializer, ReviewCreateUpdateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .permissions import IsReviewAuthorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """
    A viewset for publishing, reading, and managing property reviews.

    Provides public access to view ratings and feedback while enforcing strict business
    logic boundaries for data modifications. Leverages optimized SQL joins via select_related
    to eliminate the N+1 query problem across Booking, User, and Listing relations.

    Access Restrictions:
        - List / Retrieve: Publicly accessible to all users and anonymous guests.
        - Create: Limited to authenticated Tenants who have a fully completed booking history.
        - Update / Destroy: Guarded by custom object-level permissions. Restricted strictly
          to the original review author (Tenant) or system Administrators.
    """

    queryset = Review.all_objects.select_related('booking', 'booking__user', 'booking__listing').all()
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
        'booking__listing': ['exact'],
        'booking': ['exact']
    }
    ordering_fields = [
        'property_rating', 'location_rating', 'created_at'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.queryset
        return Review.objects.select_related('booking', 'booking__user', 'booking__listing').all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewAuthorOrAdmin()]
        return super().get_permissions()