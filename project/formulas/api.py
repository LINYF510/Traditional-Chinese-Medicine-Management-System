from django.db import transaction
from rest_framework import permissions, serializers, viewsets

from accounts.api_permissions import RBACPermission

from .models import Formula, FormulaItem


class FormulaItemReadSerializer(serializers.ModelSerializer):
    herb_name = serializers.CharField(source="herb.herb_name", read_only=True)
    herb_code = serializers.CharField(source="herb.herb_code", read_only=True)

    class Meta:
        model = FormulaItem
        fields = [
            "id",
            "herb",
            "herb_name",
            "herb_code",
            "dosage",
            "dosage_unit",
            "role_in_formula",
            "sort_no",
            "remark",
        ]


class FormulaItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormulaItem
        fields = ["herb", "dosage", "dosage_unit", "role_in_formula", "sort_no", "remark"]


class FormulaSerializer(serializers.ModelSerializer):
    items = FormulaItemWriteSerializer(many=True, required=False)
    items_detail = FormulaItemReadSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Formula
        fields = [
            "id",
            "formula_code",
            "formula_name",
            "source",
            "efficacy",
            "indication",
            "usage_method",
            "contraindication",
            "remark",
            "status",
            "items",
            "items_detail",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        with transaction.atomic():
            formula = Formula.objects.create(**validated_data)
            for item_data in items_data:
                FormulaItem.objects.create(formula=formula, **item_data)
        return formula

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if items_data is not None:
                instance.items.all().delete()
                for item_data in items_data:
                    FormulaItem.objects.create(formula=instance, **item_data)
        return instance


class FormulaViewSet(viewsets.ModelViewSet):
    queryset = Formula.objects.prefetch_related("items__herb").all()
    serializer_class = FormulaSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    search_fields = ["formula_code", "formula_name", "source", "efficacy", "indication"]
    filterset_fields = ["status"]
    ordering_fields = ["formula_code", "formula_name", "created_at", "updated_at"]
    permission_code_map = {
        "list": "formula.view",
        "retrieve": "formula.view",
        "create": "formula.create",
        "update": "formula.update",
        "partial_update": "formula.update",
        "destroy": "formula.delete",
    }
