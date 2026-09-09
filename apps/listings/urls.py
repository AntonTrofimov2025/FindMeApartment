from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.listings.views import ListingViewSet


router = SimpleRouter()
router.register('listings', ListingViewSet, basename='listing')


urlpatterns = [
    path('', include(router.urls))
]

