from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if any((
            request.method in permissions.SAFE_METHODS,
            request.method == "POST"
        )):
            return True
        if all((
            request.method in ["DELETE", "PATCH"],
            request.user == obj.author
        )):
            return True
        return False
