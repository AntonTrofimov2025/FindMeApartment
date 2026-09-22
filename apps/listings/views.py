from rest_framework import viewsets, status
from apps.listings.models import Listing, Photo
from .serializers import ListingSerializer, ListingCreateUpdateSerializer
from .serializers import PhotoSerializer
from rest_framework.decorators import action
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
    """
    A comprehensive ViewSet for managing real estate properties.

    Handles full CRUD lifecycle operations for property listings with dynamic serialization
    and advanced query filtering. Integrates multi-role visibility boundaries:

    Queryset Scopes:
        - Administrators: Gain unconditional access to all listings (active, inactive, and soft-deleted).
        - Landlords: Authorized to see their own properties in any state, plus other hosts' active ones.
        - Tenants / Guests: Restricted exclusively to active, non-deleted properties in the catalog.
    """

    queryset = Listing.all_objects.select_related('user').prefetch_related('photos').all()
    serializer_class = ListingSerializer
    permission_classes = [IsLandLordOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['title', 'description', 'city', 'district', 'street']
    filterset_class = ListingFilter
    ordering_fields = ['price_per_night', 'rooms', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ListingCreateUpdateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.queryset
        if user.is_authenticated and user.groups.filter(name='Landlord').exists():
            return Listing.all_objects.select_related('user').prefetch_related('photos').filter(
                Q(user=user) | Q(deleted_at__isnull=True, is_active=True))

        return Listing.all_objects.select_related('user').prefetch_related(
            'photos').filter(deleted_at__isnull=True, is_active=True)

    @extend_schema(
        summary="Use to toggle the listing active status by providing its id",
        description="Allow to activate/deactivate the specified listing (Hides from catalog).",
        request=None
    )
    @action(detail=True, methods=['post'], url_name='toggle_is_active', url_path='toggle')
    def toggle_is_active(self, request, *args, **kwargs):
        """
        Toggle the activation flag (`is_active`) of a property listing.

        Enables hosts to instantly hide their listings from the public search catalog
        or make them visible again. Aborts execution with a 400 Bad Request if the
        target property has already been soft-deleted.

        Permissions:
            - Restriced to the property owner or system Administrators.
        """
        listing = self.get_object()

        if listing.is_deleted:
            return Response({'msg': 'Cannot toggle active status on a deleted listing!'},
                            status=status.HTTP_400_BAD_REQUEST)

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
    """
    A ViewSet for uploading and managing property media content.

    Supports multipart file processing to upload property images into isolated directories.
    Enforces strict file extension whitelist checks and a 2 MB maximum file size constraint.

    Permissions:
        - Read: Anyone (SAFE_METHODS).
        - Create / Destroy: Bound tightly to the Landlord who owns the underlying property asset.
        - Update: Locked globally to global Administrators only to protect metadata history integrity.
    """

    queryset = Photo.all_objects.select_related('listing').all()
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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.queryset

        if user.is_authenticated and user.groups.filter(name='Landlord').exists():
            return Photo.all_objects.select_related('listing').filter(
                Q(listing__user=user) | Q(listing__deleted_at__isnull=True, listing__is_active=True))

        return Photo.objects.select_related('listing').filter(listing__is_active=True)

    def perform_create(self, serializer):
        listing = serializer.validated_data.get('listing')

        if listing.user != self.request.user and not self.request.user.is_staff and not self.request.user.is_superuser:
            raise PermissionDenied({'detail': 'You are not the owner of this property to be allowed to modify photos!'})

        serializer.save()

    def perform_destroy(self, instance):
        if instance.listing.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied({'detail': 'You are not allowed to delete photos from not your own listings!'})

        instance.delete()

