from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from .models import InventoryRecord, InventoryStock, InventoryWarning


def ensure_stock(herb) -> InventoryStock:
    stock, _ = InventoryStock.objects.get_or_create(
        herb=herb,
        defaults={"unit": herb.unit, "safe_quantity": Decimal("0"), "current_quantity": Decimal("0")},
    )
    if not stock.unit:
        stock.unit = herb.unit
        stock.save(update_fields=["unit", "updated_at"])
    return stock


@transaction.atomic
def inbound(*, herb, quantity: Decimal, operator=None, remark: str = "") -> InventoryRecord:
    if quantity <= 0:
        raise ValueError("入库数量必须大于 0")

    stock = ensure_stock(herb)
    before = stock.current_quantity
    after = before + quantity
    stock.current_quantity = after
    stock.sync_status()
    stock.save()
    record = InventoryRecord.objects.create(
        herb=herb,
        record_type=InventoryRecord.TYPE_INBOUND,
        quantity=quantity,
        before_quantity=before,
        after_quantity=after,
        operator=operator,
        business_no=f"IN-{uuid4().hex[:8].upper()}",
        remark=remark,
    )
    sync_warning(stock)
    return record


@transaction.atomic
def outbound(*, herb, quantity: Decimal, operator=None, remark: str = "") -> InventoryRecord:
    if quantity <= 0:
        raise ValueError("出库数量必须大于 0")

    stock = ensure_stock(herb)
    if stock.current_quantity < quantity:
        raise ValueError("库存不足")

    before = stock.current_quantity
    after = before - quantity
    stock.current_quantity = after
    stock.sync_status()
    stock.save()
    record = InventoryRecord.objects.create(
        herb=herb,
        record_type=InventoryRecord.TYPE_OUTBOUND,
        quantity=quantity,
        before_quantity=before,
        after_quantity=after,
        operator=operator,
        business_no=f"OUT-{uuid4().hex[:8].upper()}",
        remark=remark,
    )
    sync_warning(stock)
    return record


@transaction.atomic
def stock_check(*, herb, checked_quantity: Decimal, operator=None, remark: str = "") -> InventoryRecord:
    if checked_quantity < 0:
        raise ValueError("盘点库存不能为负数")

    stock = ensure_stock(herb)
    before = stock.current_quantity
    delta = checked_quantity - before
    stock.current_quantity = checked_quantity
    stock.sync_status()
    stock.save()
    record = InventoryRecord.objects.create(
        herb=herb,
        record_type=InventoryRecord.TYPE_CHECK,
        quantity=delta,
        before_quantity=before,
        after_quantity=checked_quantity,
        operator=operator,
        business_no=f"CHK-{uuid4().hex[:8].upper()}",
        remark=remark,
    )
    sync_warning(stock)
    return record


def sync_warning(stock: InventoryStock) -> None:
    is_low = stock.current_quantity < stock.safe_quantity
    active_warning = (
        InventoryWarning.objects.filter(
            herb=stock.herb,
            warning_status=InventoryWarning.STATUS_ACTIVE,
        )
        .order_by("-generated_at")
        .first()
    )

    if is_low:
        if active_warning:
            active_warning.current_quantity = stock.current_quantity
            active_warning.safe_quantity = stock.safe_quantity
            active_warning.save(update_fields=["current_quantity", "safe_quantity"])
        else:
            InventoryWarning.objects.create(
                herb=stock.herb,
                current_quantity=stock.current_quantity,
                safe_quantity=stock.safe_quantity,
            )
        return

    if active_warning:
        active_warning.warning_status = InventoryWarning.STATUS_RESOLVED
        active_warning.resolved_at = timezone.now()
        active_warning.current_quantity = stock.current_quantity
        active_warning.safe_quantity = stock.safe_quantity
        active_warning.save(
            update_fields=[
                "warning_status",
                "resolved_at",
                "current_quantity",
                "safe_quantity",
            ]
        )
