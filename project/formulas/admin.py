from django.contrib import admin

from .models import Formula, FormulaItem


class FormulaItemInline(admin.TabularInline):
    model = FormulaItem
    extra = 1


@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display = ("formula_code", "formula_name", "source", "status")
    list_filter = ("status", "source")
    search_fields = ("formula_code", "formula_name", "source", "efficacy", "indication")
    inlines = [FormulaItemInline]


@admin.register(FormulaItem)
class FormulaItemAdmin(admin.ModelAdmin):
    list_display = ("formula", "herb", "dosage", "dosage_unit", "role_in_formula", "sort_no")
    list_filter = ("role_in_formula",)
    search_fields = ("formula__formula_name", "herb__herb_name")

# Register your models here.
