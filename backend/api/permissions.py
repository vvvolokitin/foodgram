from rest_framework.permissions import SAFE_METHODS, BasePermission

# from core.constants_users import ADMIN


class IsAdminOrReadOnly(BasePermission):
    """Проврека администратор или безопасный метод."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class IsAuthorAdminOrReadOnly(BasePermission):
    """Проврека автор, администратор или безопасный метод."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            # or request.user.role == ADMIN
            or request.user.is_superuser
        )
