from django.contrib import admin

from .models import InventoryRecord, InventoryStock, InventoryWarning


@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = (
        "herb",
        "current_quantity",
        "safe_quantity",
        "unit",
        "stock_status",
        "updated_at",
    )
    list_filter = ("stock_status",)
    search_fields = ("herb__herb_name", "herb__herb_code", "warehouse_location")


@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "herb",
        "record_type",
        "quantity",
        "before_quantity",
        "after_quantity",
        "operator",
    )
    list_filter = ("record_type",)
    search_fields = ("herb__herb_name", "business_no", "remark")


@admin.register(InventoryWarning)
class InventoryWarningAdmin(admin.ModelAdmin):
    list_display = (
        "herb",
        "warning_type",
        "current_quantity",
        "safe_quantity",
        "warning_status",
        "generated_at",
        "resolved_at",
    )
    list_filter = ("warning_status", "warning_type")
    search_fields = ("herb__herb_name", "herb__herb_code")

# Register your models here.
