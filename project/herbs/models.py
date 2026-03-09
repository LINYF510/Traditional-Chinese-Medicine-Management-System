from django.db import models


class Herb(models.Model):
    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = (
        (STATUS_ENABLED, "启用"),
        (STATUS_DISABLED, "停用"),
    )

    herb_code = models.CharField("药材编号", max_length=50, unique=True)
    herb_name = models.CharField("药材名称", max_length=100)
    alias_name = models.CharField("别名", max_length=100, blank=True)
    category = models.CharField("分类", max_length=50)
    nature_taste = models.CharField("性味", max_length=100, blank=True)
    meridian_tropism = models.CharField("归经", max_length=100, blank=True)
    efficacy = models.TextField("功效", blank=True)
    indication = models.TextField("主治", blank=True)
    origin_place = models.CharField("产地", max_length=100, blank=True)
    storage_method = models.CharField("储存方式", max_length=255, blank=True)
    unit = models.CharField("单位", max_length=20, default="g")
    reference_price = models.DecimalField("参考价格", max_digits=10, decimal_places=2, default=0)
    description = models.TextField("药材描述", blank=True)
    extra_attributes = models.JSONField("扩展属性", default=dict, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default=STATUS_ENABLED)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "中药材"
        verbose_name_plural = "中药材"
        ordering = ["herb_code"]
        indexes = [
            models.Index(fields=["herb_name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.herb_name} ({self.herb_code})"
