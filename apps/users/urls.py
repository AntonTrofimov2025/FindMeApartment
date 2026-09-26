from django.urls import path, include
from .views import UserCreateGenericView, UserReadOnlyViewSet, logout, UserMeView, UserBecomeLandlordView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', UserReadOnlyViewSet, basename='user')


urlpatterns = [
    path('auth/register/', UserCreateGenericView.as_view(), name='user-create-view'),
    path('auth/logout/', logout, name='logout-view'),
    path('users/me/', UserMeView.as_view(), name='user-profile-view'),
    path('users/me/become-landlord/', UserBecomeLandlordView.as_view(), name='user-become-landlord-view'),
    path('', include(router.urls))
]

