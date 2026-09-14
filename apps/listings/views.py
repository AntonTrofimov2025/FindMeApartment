from rest_framework import viewsets
from apps.listings.models import Listing, Photo
from .serializers import ListingSerializer, ListingCreateUpdateSerializer
from .serializers import PhotoSerializer
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.listings.filters.listing_filter import ListingFilter
from apps.listings.permissions import IsLandLordOrReadOnly
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q

@extend_schema_view(
    list=extend_schema(summary='Get all listings', description='List of all listings'),
    create=extend_schema(summary='Create new listing', description='New listing creation'),
    update=extend_schema(summary='Update existing listing', description='Update of listing'),
    retrieve=extend_schema(summary='Get specific listing', description='Retrival of one specific listing'),
    partial_update=extend_schema(summary='Update existing listing partially', description='Partial listing update'),
    destroy=extend_schema(summary='Delete specific listing', description='Deletion of one specific listing')
)
class ListingViewSet(viewsets.ModelViewSet):

    queryset = Listing.objects.select_related('user').all()
    serializer_class = ListingSerializer
    permission_classes = [IsLandLordOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['title', 'description', 'city', 'district', 'street']
    filterset_class = ListingFilter
    ordering_fields = ['price_per_night', 'rooms', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateUpdateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.queryset
        if user.is_authenticated and user.groups.filter(name='Landlord').exists():
            return Listing.objects.select_related('user').filter(Q(user=user) | Q(is_active=True))

        return Listing.objects.select_related('user').filter(is_active=True)

    @extend_schema(
        summary="Use to toggle the listing active status by providing its id",
        description="Allow to activate/deactivate the specified listing (Hides from catalog)."
    )
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

@extend_schema_view(
    list=extend_schema(summary='Get all photos', description='List of all photos'),
    create=extend_schema(summary='Create new photo', description='New photo creation'),
    update=extend_schema(summary='Update existing photo', description='Update of photo'),
    retrieve=extend_schema(summary='Get specific photo', description='Retrival of one specific photo'),
    partial_update=extend_schema(summary='Update existing photo partially', description='Partial photo update'),
    destroy=extend_schema(summary='Delete specific photo', description='Deletion of one specific photo')
)
class PhotoViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.select_related('listing').all()
    serializer_class = PhotoSerializer
    permission_classes = [IsLandLordOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['photo_number', 'listing__title']
    filterset_fields = {
        'photo_number': ['exact', 'gte', 'lte'],
        'listing': ['exact']
    }
    ordering_fields = ['listing', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        listing = serializer.validated_data.get('listing')

        if listing.user != self.request.user and not self.request.user.is_staff and not self.request.user.is_superuser:
            raise PermissionDenied({'detail': 'You are not the owner of this property to be allowed to modify photos!'})

        serializer.save()

    def perform_destroy(self, instance):
        if instance.listing.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied({'detail': 'You are not allowed to delete photos from not your own listings!'})

        instance.delete()

