from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from apps.bookings.permissions import IsLandLord
from rest_framework.generics import get_object_or_404
from .models import Booking
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.core.models import StatusChoices
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .serializers.bookings import BookingSerializer, BookingCreateUpdateSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(summary='Approve booking', description='Approval of booking provided its status is PENDING')
@api_view(['POST'])
@permission_classes([IsLandLord])
def booking_approve(request, pk, *args, **kwargs):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user != booking.listing.user:
        raise PermissionDenied({'detail': 'You are not the owner of this property!'})
    if booking.booking_status != StatusChoices.PENDING:
        raise ValidationError({'detail': 'The booking status must be PENDING only to be approved!'})
    booking.booking_status = StatusChoices.CONFIRMED
    booking.save()
    return Response({'msg': 'The booking has successfully been confirmed.'}, status=status.HTTP_200_OK)

@extend_schema(summary='Reject booking', description='Rejection of booking, provided its status is PENDING')
@api_view(['POST'])
@permission_classes([IsLandLord])
def booking_reject(request, pk, *args, **kwargs):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user != booking.listing.user:
        raise PermissionDenied({'detail': 'You are not the owner of this property!'})
    if booking.booking_status != StatusChoices.PENDING:
        raise ValidationError({'detail': 'The booking status must be PENDING only to be rejected!'})
    booking.booking_status = StatusChoices.REJECTED
    booking.save()
    return Response({'msg': 'The booking has successfully been rejected.'}, status=status.HTTP_200_OK)

@extend_schema(summary='Cancel booking', description='Cancellation of booking provided its status is CONFIRMED')
@api_view(['POST'])
@permission_classes([IsLandLord])
def booking_cancel(request, pk, *args, **kwargs):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user != booking.listing.user:
        raise PermissionDenied({'detail': 'You are not the owner of this property!'})
    if booking.booking_status != StatusChoices.CONFIRMED:
        raise ValidationError({'detail': 'The booking status must be CONFIRMED only to be cancelled!'})
    booking.booking_status = StatusChoices.CANCELLED
    booking.save()
    return Response({'msg': 'The booking has successfully been cancelled.'}, status=status.HTTP_200_OK)

@extend_schema_view(
    list=extend_schema(summary='Get all bookings', description='List of all bookings'),
    create=extend_schema(summary='Create new booking', description='New booking creation'),
    update=extend_schema(summary='Update existing booking', description='Update of booking'),
    retrieve=extend_schema(summary='Get specific booking', description='Retrival of one specific booking'),
    partial_update=extend_schema(summary='Update existing booking partially', description='Partial booking update'),
    destroy=extend_schema(summary='Delete specific booking', description='Deletion of one specific booking')
)
class BookingViewSet(viewsets.ModelViewSet):

    queryset = Booking.objects.select_related('user', 'listing').all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = [
        'listing__title', 'listing__city', 'user__first_name', 'user__last_name', 'user__email'
    ]
    filterset_fields = {
        'booking_status': ['exact', 'in'],
        'date_from': ['exact', 'gte', 'lte'],
        'date_to': ['exact', 'gte', 'lte'],
        'listing': ['exact']
    }
    ordering_fields = [
        'date_from', 'total_price', 'created_at'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateUpdateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Booking.objects.select_related('user', 'listing').all()

        if user.groups.filter(name='Landlord').exists():
            return Booking.objects.select_related('user', 'listing').filter(listing__user=user)

        return Booking.objects.select_related('user', 'listing').filter(user=user)

