from django.contrib import admin

from .models import Herb


@admin.register(Herb)
class HerbAdmin(admin.ModelAdmin):
    list_display = (
        "herb_code",
        "herb_name",
        "category",
        "unit",
        "reference_price",
        "status",
    )
    list_filter = ("category", "status")
    search_fields = ("herb_code", "herb_name", "alias_name", "efficacy", "indication")

# Register your models here.
