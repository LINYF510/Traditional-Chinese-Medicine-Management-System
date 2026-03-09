from rest_framework.permissions import BasePermission

from .rbac import user_has_permission


class RBACPermission(BasePermission):
    """
    Requires authenticated user and checks permission code mapped on views.

    View can define one of:
    - permission_code = "module.action"
    - permission_code_map = {"list": "...", "create": "..."} for ViewSet actions
    - permission_code_map = {"GET": "...", "POST": "..."} for APIView methods
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        permission_code = self._resolve_permission_code(request, view)
        return user_has_permission(user, permission_code)

    def _resolve_permission_code(self, request, view) -> str:
        explicit = getattr(view, "permission_code", "")
        if explicit:
            return explicit

        mapping = getattr(view, "permission_code_map", {})
        if not mapping:
            return ""

        action = getattr(view, "action", "")
        if action and action in mapping:
            return mapping[action]

        method = request.method.upper()
        return mapping.get(method, "")
