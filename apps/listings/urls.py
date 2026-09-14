from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.listings.views import ListingViewSet, PhotoViewSet


router = SimpleRouter()
router.register('listings', ListingViewSet, basename='listing')
router.register('photos', PhotoViewSet, basename='photo')


urlpatterns = [
    path('', include(router.urls))
]

