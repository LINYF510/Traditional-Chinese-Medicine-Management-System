from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OperationLog, PermissionEntry, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("role_code", "role_name", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("role_code", "role_name")


@admin.register(PermissionEntry)
class PermissionEntryAdmin(admin.ModelAdmin):
    list_display = ("permission_code", "permission_name", "permission_type")
    list_filter = ("permission_type",)
    search_fields = ("permission_code", "permission_name", "path")
    filter_horizontal = ("roles",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "display_name",
        "role",
        "is_staff",
        "is_active",
        "last_login",
    )
    list_filter = ("is_staff", "is_active", "role")
    search_fields = ("username", "real_name", "email", "phone")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "业务信息",
            {
                "fields": ("real_name", "gender", "phone", "role"),
            },
        ),
    )


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "module_name",
        "operation_type",
        "user",
        "operation_result",
        "ip_address",
    )
    list_filter = ("module_name", "operation_type", "operation_result")
    search_fields = ("request_url", "request_param", "ip_address")
    readonly_fields = (
        "created_at",
        "user",
        "module_name",
        "operation_type",
        "request_method",
        "request_url",
        "request_param",
        "operation_result",
        "ip_address",
    )

# Register your models here.
