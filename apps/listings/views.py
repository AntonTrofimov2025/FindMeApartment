from rest_framework import viewsets
from apps.listings.models import Listing
from .serializers.listings import ListingSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.listings.filters.listing_filter import ListingFilter


class ListingViewSet(viewsets.ModelViewSet):

    queryset = Listing.objects.select_related('user').all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    filterset_class = ListingFilter
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingSerializer # 'ВРЕМЕННО! ЗАМЕНИ НА БУДУЩИЙ CREATE SERIALIZER' #
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_name='toggle_is_active', url_path='toggle')
    def toggle_is_active(self, request, *args, **kwargs):
        listing = self.get_object()

        if listing.user != request.user and not request.user.is_staff:
            raise PermissionDenied('You are not allowed to manage this listing!')

        listing.is_active = not listing.is_active
        listing.save(update_fields=['is_active'])
        return Response({'id': listing.id, 'is_active': listing.is_active,
                         'msg': f"Status has been changed to {'active' if listing.is_active else 'not active'}"},
                        status=status.HTTP_200_OK)

