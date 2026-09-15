from django.urls import path, include
from .views import booking_approve, booking_cancel, booking_reject, booking_check_in
from rest_framework.routers import SimpleRouter
from .views import BookingViewSet

router = SimpleRouter()
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('bookings/<uuid:pk>/approve/', booking_approve, name='booking-approve-view'),
    path('bookings/<uuid:pk>/cancel/', booking_cancel, name='booking-cancel-view'),
    path('bookings/<uuid:pk>/reject/', booking_reject, name='booking-reject-view'),
    path('bookings/<uuid:pk>/check_in/', booking_check_in, name='booking-check-in-view'),
    path('', include(router.urls) )
]

