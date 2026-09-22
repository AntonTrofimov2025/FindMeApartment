from rest_framework import permissions


class IsLandLordOrReadOnly(permissions.BasePermission):
    message = "Only Landlords can access this resource!"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return request.user.is_staff or request.user.groups.filter(name='Landlord').exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.user == request.user

