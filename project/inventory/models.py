from django.conf import settings
from django.db import models

from herbs.models import Herb


class InventoryStock(models.Model):
    STATUS_NORMAL = "normal"
    STATUS_LOW = "low"
    STATUS_EMPTY = "empty"
    STATUS_CHOICES = (
        (STATUS_NORMAL, "安全"),
        (STATUS_LOW, "低库存"),
        (STATUS_EMPTY, "缺货"),
    )

    herb = models.OneToOneField(
        Herb,
        verbose_name="药材",
        on_delete=models.CASCADE,
        related_name="stock",
    )
    current_quantity = models.DecimalField("当前库存", max_digits=10, decimal_places=2, default=0)
    safe_quantity = models.DecimalField("安全库存", max_digits=10, decimal_places=2, default=0)
    unit = models.CharField("单位", max_length=20, default="g")
    warehouse_location = models.CharField("仓位", max_length=100, blank=True)
    stock_status = models.CharField("库存状态", max_length=20, choices=STATUS_CHOICES, default=STATUS_NORMAL)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "库存"
        verbose_name_plural = "库存"
        ordering = ["herb__herb_code"]
        indexes = [models.Index(fields=["stock_status"]), models.Index(fields=["updated_at"])]

    def sync_status(self) -> None:
        if self.current_quantity <= 0:
            self.stock_status = self.STATUS_EMPTY
        elif self.current_quantity < self.safe_quantity:
            self.stock_status = self.STATUS_LOW
        else:
            self.stock_status = self.STATUS_NORMAL

    def __str__(self) -> str:
        return f"{self.herb.herb_name}: {self.current_quantity}{self.unit}"


class InventoryRecord(models.Model):
    TYPE_INBOUND = "inbound"
    TYPE_OUTBOUND = "outbound"
    TYPE_CHECK = "check"
    RECORD_TYPES = (
        (TYPE_INBOUND, "入库"),
        (TYPE_OUTBOUND, "出库"),
        (TYPE_CHECK, "盘点"),
    )

    herb = models.ForeignKey(
        Herb,
        verbose_name="药材",
        on_delete=models.PROTECT,
        related_name="inventory_records",
    )
    record_type = models.CharField("类型", max_length=20, choices=RECORD_TYPES)
    quantity = models.DecimalField("变更数量", max_digits=10, decimal_places=2)
    before_quantity = models.DecimalField("变更前库存", max_digits=10, decimal_places=2)
    after_quantity = models.DecimalField("变更后库存", max_digits=10, decimal_places=2)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="操作人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inventory_records",
    )
    business_no = models.CharField("业务单号", max_length=50, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "库存流水"
        verbose_name_plural = "库存流水"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["record_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["herb", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.herb.herb_name}-{self.get_record_type_display()}-{self.quantity}"


class InventoryWarning(models.Model):
    TYPE_SHORTAGE = "shortage"
    TYPE_CHOICES = ((TYPE_SHORTAGE, "库存不足"),)

    STATUS_ACTIVE = "active"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "生效中"),
        (STATUS_RESOLVED, "已解除"),
    )

    herb = models.ForeignKey(
        Herb,
        verbose_name="药材",
        on_delete=models.CASCADE,
        related_name="inventory_warnings",
    )
    warning_type = models.CharField("预警类型", max_length=20, choices=TYPE_CHOICES, default=TYPE_SHORTAGE)
    current_quantity = models.DecimalField("当前库存", max_digits=10, decimal_places=2, default=0)
    safe_quantity = models.DecimalField("安全库存", max_digits=10, decimal_places=2, default=0)
    warning_status = models.CharField(
        "预警状态", max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    generated_at = models.DateTimeField("生成时间", auto_now_add=True)
    resolved_at = models.DateTimeField("解除时间", null=True, blank=True)

    class Meta:
        verbose_name = "库存预警"
        verbose_name_plural = "库存预警"
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["warning_status"]),
            models.Index(fields=["generated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.herb.herb_name}-{self.get_warning_status_display()}"
