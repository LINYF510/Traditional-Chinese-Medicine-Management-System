from django.db import models

from herbs.models import Herb


class Formula(models.Model):
    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = (
        (STATUS_ENABLED, "启用"),
        (STATUS_DISABLED, "停用"),
    )

    formula_code = models.CharField("方剂编号", max_length=50, unique=True)
    formula_name = models.CharField("方剂名称", max_length=100)
    source = models.CharField("来源", max_length=100, blank=True)
    efficacy = models.TextField("功效", blank=True)
    indication = models.TextField("主治", blank=True)
    usage_method = models.TextField("用法用量", blank=True)
    contraindication = models.TextField("禁忌说明", blank=True)
    remark = models.CharField("备注", max_length=255, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default=STATUS_ENABLED)
    herbs = models.ManyToManyField(Herb, through="FormulaItem", related_name="formulas")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "方剂"
        verbose_name_plural = "方剂"
        ordering = ["formula_code"]
        indexes = [models.Index(fields=["formula_name"]), models.Index(fields=["status"])]

    def __str__(self) -> str:
        return f"{self.formula_name} ({self.formula_code})"


class FormulaItem(models.Model):
    ROLE_JUN = "jun"
    ROLE_CHEN = "chen"
    ROLE_ZUO = "zuo"
    ROLE_SHI = "shi"
    ROLE_CHOICES = (
        (ROLE_JUN, "君"),
        (ROLE_CHEN, "臣"),
        (ROLE_ZUO, "佐"),
        (ROLE_SHI, "使"),
    )

    formula = models.ForeignKey(
        Formula,
        verbose_name="方剂",
        on_delete=models.CASCADE,
        related_name="items",
    )
    herb = models.ForeignKey(
        Herb,
        verbose_name="药材",
        on_delete=models.PROTECT,
        related_name="formula_items",
    )
    dosage = models.DecimalField("剂量", max_digits=10, decimal_places=2)
    dosage_unit = models.CharField("剂量单位", max_length=20, default="g")
    role_in_formula = models.CharField("君臣佐使", max_length=20, choices=ROLE_CHOICES, blank=True)
    sort_no = models.PositiveIntegerField("排序号", default=0)
    remark = models.CharField("备注", max_length=255, blank=True)

    class Meta:
        verbose_name = "方剂组成"
        verbose_name_plural = "方剂组成"
        ordering = ["sort_no", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["formula", "herb"],
                name="uniq_formula_herb_item",
            )
        ]

    def __str__(self) -> str:
        return f"{self.formula.formula_name} - {self.herb.herb_name} {self.dosage}{self.dosage_unit}"
