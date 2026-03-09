from __future__ import annotations

from dataclasses import dataclass

from .rbac import user_has_permission


@dataclass(frozen=True)
class MenuItem:
    label: str
    icon: str
    permission_code: str
    path: str


MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem(label="仪表盘", icon="dashboard", permission_code="dashboard.view", path="/app/dashboard"),
    MenuItem(label="药材管理", icon="psychiatry", permission_code="herb.view", path="/app/herbs"),
    MenuItem(label="方剂管理", icon="science", permission_code="formula.view", path="/app/formulas"),
    MenuItem(label="库存管理", icon="inventory_2", permission_code="inventory.view", path="/app/inventory"),
)


def build_visible_menu(user) -> list[dict]:
    if not getattr(user, "is_authenticated", False):
        return []
    return [
        {
            "label": item.label,
            "icon": item.icon,
            "permission_code": item.permission_code,
            "path": item.path,
        }
        for item in MENU_ITEMS
        if user_has_permission(user, item.permission_code)
    ]
