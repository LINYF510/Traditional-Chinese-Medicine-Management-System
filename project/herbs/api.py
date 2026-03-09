from rest_framework import permissions, serializers, viewsets

from accounts.api_permissions import RBACPermission

from .models import Herb


class HerbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Herb
        fields = [
            "id",
            "herb_code",
            "herb_name",
            "alias_name",
            "category",
            "nature_taste",
            "meridian_tropism",
            "efficacy",
            "indication",
            "origin_place",
            "storage_method",
            "unit",
            "reference_price",
            "description",
            "extra_attributes",
            "status",
            "created_at",
            "updated_at",
        ]


class HerbViewSet(viewsets.ModelViewSet):
    queryset = Herb.objects.all()
    serializer_class = HerbSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    search_fields = ["herb_code", "herb_name", "alias_name", "efficacy", "indication"]
    filterset_fields = ["category", "status"]
    ordering_fields = ["herb_code", "herb_name", "reference_price", "created_at", "updated_at"]
    permission_code_map = {
        "list": "herb.view",
        "retrieve": "herb.view",
        "create": "herb.create",
        "update": "herb.update",
        "partial_update": "herb.update",
        "destroy": "herb.delete",
    }
