from rest_framework import permissions



class IsReviewAuthorOrAdmin(permissions.BasePermission):
    """
    Custom permission to ensure that only the original author of the review
    (the Tenant who made the booking) or a system Administrator can modify or delete it.
    """

    message = "Only Review Authors or Admins can modify this review!"

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.booking.user == request.user