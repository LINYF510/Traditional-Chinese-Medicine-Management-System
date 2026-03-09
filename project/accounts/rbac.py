def user_has_permission(user, permission_code: str) -> bool:
    if not permission_code:
        return True
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "role", None) is not None and not user.role.status and not user.is_superuser:
        return False
    return user.has_permission_code(permission_code)
