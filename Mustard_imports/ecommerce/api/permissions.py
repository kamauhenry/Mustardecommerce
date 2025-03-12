from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only owners of an object or admin users to access it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to grant access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
