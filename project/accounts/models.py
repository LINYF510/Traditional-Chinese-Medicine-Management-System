from django.contrib.auth.models import AbstractUser
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


class Role(TimestampedModel):
    role_name = models.CharField("角色名称", max_length=50)
    role_code = models.CharField("角色编码", max_length=50, unique=True)
    description = models.CharField("描述", max_length=255, blank=True)
    status = models.BooleanField("启用状态", default=True)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ["role_code"]

    def __str__(self) -> str:
        return f"{self.role_name}({self.role_code})"


class PermissionEntry(models.Model):
    TYPE_MENU = "menu"
    TYPE_BUTTON = "button"
    TYPE_API = "api"
    PERMISSION_TYPES = (
        (TYPE_MENU, "菜单"),
        (TYPE_BUTTON, "按钮"),
        (TYPE_API, "接口"),
    )

    permission_name = models.CharField("权限名称", max_length=100)
    permission_code = models.CharField("权限标识", max_length=100, unique=True)
    permission_type = models.CharField("权限类型", max_length=20, choices=PERMISSION_TYPES)
    path = models.CharField("路径", max_length=255, blank=True)
    description = models.CharField("描述", max_length=255, blank=True)
    roles = models.ManyToManyField(Role, related_name="permission_entries", blank=True)

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = "权限"
        ordering = ["permission_code"]

    def __str__(self) -> str:
        return f"{self.permission_name}({self.permission_code})"


class User(AbstractUser, TimestampedModel):
    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDERS = (
        (GENDER_MALE, "男"),
        (GENDER_FEMALE, "女"),
        (GENDER_OTHER, "其他"),
    )

    real_name = models.CharField("真实姓名", max_length=50, blank=True)
    gender = models.CharField("性别", max_length=10, choices=GENDERS, blank=True)
    phone = models.CharField("手机号", max_length=20, blank=True)
    role = models.ForeignKey(
        Role,
        verbose_name="角色",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["is_active"]),
        ]

    @property
    def display_name(self) -> str:
        return self.real_name or self.get_full_name() or self.username

    def get_permission_codes(self) -> set[str]:
        if not self.is_authenticated:
            return set()
        cached = getattr(self, "_cached_permission_codes", None)
        if cached is not None:
            return cached
        if self.is_superuser:
            codes = set(PermissionEntry.objects.values_list("permission_code", flat=True))
        elif not self.role_id:
            codes = set()
        else:
            codes = set(self.role.permission_entries.values_list("permission_code", flat=True))
        self._cached_permission_codes = codes
        return codes

    def has_permission_code(self, code: str) -> bool:
        if not code:
            return True
        if self.is_superuser:
            return True
        return code in self.get_permission_codes()

    def __str__(self) -> str:
        return self.display_name


class OperationLog(models.Model):
    RESULT_SUCCESS = "success"
    RESULT_FAILED = "failed"
    RESULT_CHOICES = (
        (RESULT_SUCCESS, "成功"),
        (RESULT_FAILED, "失败"),
    )

    user = models.ForeignKey(
        "accounts.User",
        verbose_name="操作用户",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operation_logs",
    )
    module_name = models.CharField("模块", max_length=50)
    operation_type = models.CharField("操作类型", max_length=50)
    request_method = models.CharField("请求方法", max_length=10, blank=True)
    request_url = models.CharField("请求路径", max_length=255, blank=True)
    request_param = models.TextField("请求参数", blank=True)
    operation_result = models.CharField(
        "操作结果", max_length=20, choices=RESULT_CHOICES, default=RESULT_SUCCESS
    )
    ip_address = models.CharField("IP地址", max_length=50, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module_name"]),
            models.Index(fields=["operation_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.module_name}-{self.operation_type}-{self.created_at:%Y-%m-%d %H:%M:%S}"
