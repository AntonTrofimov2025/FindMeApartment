from rest_framework import permissions


class IsLandLordOrReadOnly(permissions.BasePermission):
    message = "Only Landlords can access this resource!"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return request.user.is_staff or request.user.groups.filter(name='landlord').exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        return obj.user == request.user

