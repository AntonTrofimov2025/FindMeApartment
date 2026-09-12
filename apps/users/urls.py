from django.urls import path, include
from .views import UserCreateGenericView, UserReadOnlyGenericView, logout
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', UserReadOnlyGenericView, basename='user')


urlpatterns = [
    path('api/auth/register/', UserCreateGenericView.as_view(), name='user-create-view'),
    path('api/auth/logout/', logout, name='logout-view'),
    path('', include(router.urls))
]

