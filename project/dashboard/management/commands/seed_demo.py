from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import PermissionEntry, Role
from formulas.models import Formula, FormulaItem
from herbs.models import Herb
from inventory.services import ensure_stock, inbound, outbound, sync_warning


class Command(BaseCommand):
    help = "Seed demo data for TCM management system"

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_role, _ = Role.objects.get_or_create(
            role_code="admin",
            defaults={"role_name": "系统管理员", "description": "管理全部模块"},
        )
        pharmacist_role, _ = Role.objects.get_or_create(
            role_code="pharmacist",
            defaults={"role_name": "药剂师", "description": "药材与库存管理"},
        )
        assistant_role, _ = Role.objects.get_or_create(
            role_code="assistant",
            defaults={"role_name": "医护人员", "description": "只读查询"},
        )

        permission_seed = [
            ("dashboard.view", "查看仪表盘", PermissionEntry.TYPE_MENU, "/"),
            ("herb.view", "查看药材", PermissionEntry.TYPE_MENU, "/herbs/"),
            ("herb.create", "新增药材", PermissionEntry.TYPE_BUTTON, "/herbs/create/"),
            ("herb.update", "编辑药材", PermissionEntry.TYPE_BUTTON, "/herbs/<id>/edit/"),
            ("herb.delete", "删除药材", PermissionEntry.TYPE_BUTTON, "/herbs/<id>/delete/"),
            ("formula.view", "查看方剂", PermissionEntry.TYPE_MENU, "/formulas/"),
            ("formula.create", "新增方剂", PermissionEntry.TYPE_BUTTON, "/formulas/create/"),
            ("formula.update", "编辑方剂", PermissionEntry.TYPE_BUTTON, "/formulas/<id>/edit/"),
            ("formula.delete", "删除方剂", PermissionEntry.TYPE_BUTTON, "/formulas/<id>/delete/"),
            ("inventory.view", "查看库存", PermissionEntry.TYPE_MENU, "/inventory/"),
            ("inventory.inbound", "库存入库", PermissionEntry.TYPE_BUTTON, "/inventory/"),
            ("inventory.outbound", "库存出库", PermissionEntry.TYPE_BUTTON, "/inventory/"),
            ("inventory.check", "库存盘点", PermissionEntry.TYPE_BUTTON, "/inventory/"),
            ("inventory.update", "库存阈值维护", PermissionEntry.TYPE_BUTTON, "/inventory/"),
            ("user.view", "查看用户", PermissionEntry.TYPE_API, "/api/users/"),
            ("user.create", "新增用户", PermissionEntry.TYPE_API, "/api/users/"),
            ("user.update", "编辑用户", PermissionEntry.TYPE_API, "/api/users/<id>/"),
            ("user.delete", "删除用户", PermissionEntry.TYPE_API, "/api/users/<id>/"),
            ("role.view", "查看角色", PermissionEntry.TYPE_API, "/api/roles/"),
            ("permission.view", "查看权限", PermissionEntry.TYPE_API, "/api/permissions/"),
        ]
        permissions = {}
        for code, name, p_type, path in permission_seed:
            perm, _ = PermissionEntry.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": name,
                    "permission_type": p_type,
                    "path": path,
                },
            )
            permissions[code] = perm

        admin_role.permission_entries.set(PermissionEntry.objects.all())
        pharmacist_role.permission_entries.set(
            [
                permissions["dashboard.view"],
                permissions["herb.view"],
                permissions["herb.create"],
                permissions["herb.update"],
                permissions["formula.view"],
                permissions["formula.create"],
                permissions["formula.update"],
                permissions["inventory.view"],
                permissions["inventory.inbound"],
                permissions["inventory.outbound"],
                permissions["inventory.check"],
                permissions["inventory.update"],
            ]
        )
        assistant_role.permission_entries.set(
            [
                permissions["dashboard.view"],
                permissions["herb.view"],
                permissions["formula.view"],
                permissions["inventory.view"],
            ]
        )

        admin_user, created = user_model.objects.get_or_create(username="admin")
        admin_user.real_name = "系统管理员"
        admin_user.role = admin_role
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.email = "admin@example.com"
        admin_user.set_password("admin123456")
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123456"))
        else:
            self.stdout.write(self.style.WARNING("Updated existing admin user to expected defaults."))

        pharmacist_user, _ = user_model.objects.get_or_create(username="pharmacist")
        pharmacist_user.real_name = "示例药剂师"
        pharmacist_user.role = pharmacist_role
        pharmacist_user.is_staff = False
        pharmacist_user.is_superuser = False
        pharmacist_user.is_active = True
        pharmacist_user.email = "pharmacist@example.com"
        pharmacist_user.set_password("pharmacist123")
        pharmacist_user.save()

        assistant_user, _ = user_model.objects.get_or_create(username="assistant")
        assistant_user.real_name = "示例医护"
        assistant_user.role = assistant_role
        assistant_user.is_staff = False
        assistant_user.is_superuser = False
        assistant_user.is_active = True
        assistant_user.email = "assistant@example.com"
        assistant_user.set_password("assistant123")
        assistant_user.save()

        herbs_seed = [
            {
                "herb_code": "H001",
                "herb_name": "人参",
                "alias_name": "Ren Shen",
                "category": "补益类",
                "nature_taste": "甘、微苦、微温",
                "meridian_tropism": "脾、肺、心经",
                "efficacy": "大补元气，复脉固脱，补脾益肺",
                "indication": "体虚欲脱，脉微欲绝，脾虚食少",
                "unit": "kg",
                "reference_price": Decimal("520.00"),
            },
            {
                "herb_code": "H002",
                "herb_name": "黄连",
                "alias_name": "Huang Lian",
                "category": "清热类",
                "nature_taste": "苦、寒",
                "meridian_tropism": "心、脾、胃、肝、胆、大肠经",
                "efficacy": "清热燥湿，泻火解毒",
                "indication": "湿热痞满，呕吐吞酸，泻痢",
                "unit": "kg",
                "reference_price": Decimal("180.00"),
            },
            {
                "herb_code": "H003",
                "herb_name": "茯苓",
                "alias_name": "Fu Ling",
                "category": "祛湿类",
                "nature_taste": "甘、淡、平",
                "meridian_tropism": "心、肺、脾、肾经",
                "efficacy": "利水渗湿，健脾宁心",
                "indication": "水肿尿少，痰饮眩悸，脾虚食少",
                "unit": "kg",
                "reference_price": Decimal("98.00"),
            },
            {
                "herb_code": "H004",
                "herb_name": "甘草",
                "alias_name": "Gan Cao",
                "category": "补益类",
                "nature_taste": "甘、平",
                "meridian_tropism": "心、肺、脾、胃经",
                "efficacy": "补脾益气，清热解毒，调和诸药",
                "indication": "脾胃虚弱，倦怠乏力，咳嗽痰多",
                "unit": "kg",
                "reference_price": Decimal("68.00"),
            },
            {
                "herb_code": "H005",
                "herb_name": "半夏",
                "alias_name": "Ban Xia",
                "category": "化痰类",
                "nature_taste": "辛、温，有毒",
                "meridian_tropism": "脾、胃、肺经",
                "efficacy": "燥湿化痰，降逆止呕，消痞散结",
                "indication": "湿痰寒痰，咳喘痰多，痰饮眩悸",
                "unit": "kg",
                "reference_price": Decimal("210.00"),
            },
        ]

        herb_map = {}
        for row in herbs_seed:
            herb, _ = Herb.objects.get_or_create(herb_code=row["herb_code"], defaults=row)
            herb_map[row["herb_code"]] = herb

        formula, _ = Formula.objects.get_or_create(
            formula_code="F001",
            defaults={
                "formula_name": "六味地黄丸",
                "source": "小儿药证直诀",
                "efficacy": "滋阴补肾",
                "indication": "头晕耳鸣，腰膝酸软，盗汗遗精",
                "usage_method": "每日2次，每次9g，温水送服",
                "contraindication": "感冒发热期间不宜使用",
                "remark": "经典补肾阴方",
            },
        )

        items_seed = [
            ("H001", Decimal("24.00"), "jun", 1),
            ("H003", Decimal("9.00"), "chen", 2),
            ("H004", Decimal("6.00"), "zuo", 3),
        ]
        for herb_code, dosage, role, sort_no in items_seed:
            FormulaItem.objects.get_or_create(
                formula=formula,
                herb=herb_map[herb_code],
                defaults={
                    "dosage": dosage,
                    "dosage_unit": "g",
                    "role_in_formula": role,
                    "sort_no": sort_no,
                },
            )

        for herb in Herb.objects.all():
            stock = ensure_stock(herb)
            if stock.current_quantity == 0:
                stock.safe_quantity = Decimal("20.00")
                stock.warehouse_location = "A-01"
                stock.save(update_fields=["safe_quantity", "warehouse_location", "updated_at"])
                inbound(herb=herb, quantity=Decimal("50.00"), operator=admin_user, remark="初始化入库")

        low_stock_herb = herb_map["H001"]
        stock = ensure_stock(low_stock_herb)
        stock.safe_quantity = Decimal("30.00")
        stock.warehouse_location = "A-24"
        stock.save(update_fields=["safe_quantity", "warehouse_location", "updated_at"])
        if stock.current_quantity > Decimal("18.00"):
            outbound(
                herb=low_stock_herb,
                quantity=stock.current_quantity - Decimal("18.00"),
                operator=admin_user,
                remark="模拟低库存场景",
            )
        sync_warning(stock)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
