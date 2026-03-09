from decimal import Decimal

from rest_framework import permissions, serializers, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api_permissions import RBACPermission
from herbs.models import Herb

from .models import InventoryRecord, InventoryStock, InventoryWarning
from .services import inbound, outbound, stock_check


class InventoryStockSerializer(serializers.ModelSerializer):
    herb_name = serializers.CharField(source="herb.herb_name", read_only=True)
    herb_code = serializers.CharField(source="herb.herb_code", read_only=True)

    class Meta:
        model = InventoryStock
        fields = [
            "id",
            "herb",
            "herb_name",
            "herb_code",
            "current_quantity",
            "safe_quantity",
            "unit",
            "warehouse_location",
            "stock_status",
            "updated_at",
        ]


class InventoryRecordSerializer(serializers.ModelSerializer):
    herb_name = serializers.CharField(source="herb.herb_name", read_only=True)
    operator_name = serializers.CharField(source="operator.display_name", read_only=True)

    class Meta:
        model = InventoryRecord
        fields = [
            "id",
            "herb",
            "herb_name",
            "record_type",
            "quantity",
            "before_quantity",
            "after_quantity",
            "operator",
            "operator_name",
            "business_no",
            "remark",
            "created_at",
        ]


class InventoryWarningSerializer(serializers.ModelSerializer):
    herb_name = serializers.CharField(source="herb.herb_name", read_only=True)

    class Meta:
        model = InventoryWarning
        fields = [
            "id",
            "herb",
            "herb_name",
            "warning_type",
            "current_quantity",
            "safe_quantity",
            "warning_status",
            "generated_at",
            "resolved_at",
        ]


class InventoryActionSerializer(serializers.Serializer):
    herb_id = serializers.PrimaryKeyRelatedField(source="herb", queryset=Herb.objects.all())
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)


class InventoryCheckSerializer(serializers.Serializer):
    herb_id = serializers.PrimaryKeyRelatedField(source="herb", queryset=Herb.objects.all())
    checked_quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)


class InventoryStockViewSet(viewsets.ModelViewSet):
    queryset = InventoryStock.objects.select_related("herb").all()
    serializer_class = InventoryStockSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    search_fields = ["herb__herb_name", "herb__herb_code", "warehouse_location"]
    filterset_fields = ["stock_status", "herb"]
    permission_code_map = {
        "list": "inventory.view",
        "retrieve": "inventory.view",
        "create": "inventory.update",
        "update": "inventory.update",
        "partial_update": "inventory.update",
        "destroy": "inventory.update",
    }


class InventoryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryRecord.objects.select_related("herb", "operator").all()
    serializer_class = InventoryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    filterset_fields = ["record_type", "herb", "operator"]
    search_fields = ["herb__herb_name", "business_no", "remark"]
    permission_code_map = {"GET": "inventory.view"}


class InventoryWarningViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryWarning.objects.select_related("herb").all()
    serializer_class = InventoryWarningSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    filterset_fields = ["warning_status", "warning_type", "herb"]
    permission_code_map = {"GET": "inventory.view"}


class InventoryInboundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    permission_code_map = {"POST": "inventory.inbound"}

    def post(self, request):
        serializer = InventoryActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            record = inbound(
                herb=serializer.validated_data["herb"],
                quantity=serializer.validated_data["quantity"],
                operator=request.user,
                remark=serializer.validated_data.get("remark", ""),
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response(InventoryRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class InventoryOutboundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    permission_code_map = {"POST": "inventory.outbound"}

    def post(self, request):
        serializer = InventoryActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            record = outbound(
                herb=serializer.validated_data["herb"],
                quantity=serializer.validated_data["quantity"],
                operator=request.user,
                remark=serializer.validated_data.get("remark", ""),
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response(InventoryRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class InventoryCheckAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    permission_code_map = {"POST": "inventory.check"}

    def post(self, request):
        serializer = InventoryCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            record = stock_check(
                herb=serializer.validated_data["herb"],
                checked_quantity=serializer.validated_data["checked_quantity"],
                operator=request.user,
                remark=serializer.validated_data.get("remark", ""),
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response(InventoryRecordSerializer(record).data, status=status.HTTP_201_CREATED)
