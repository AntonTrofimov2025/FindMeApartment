from rest_framework import permissions


class IsLandLord(permissions.BasePermission):
    message = "Only Landlords can access this resource!"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_staff or request.user.is_superuser or request.user.groups.filter(name='Landlord').exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.listing.user == request.user

