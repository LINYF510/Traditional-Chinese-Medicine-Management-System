from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import PermissionEntry, Role
from herbs.models import Herb
from inventory.models import InventoryRecord, InventoryStock, InventoryWarning


class InventoryWorkflowTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.role = Role.objects.create(role_name="库存管理员", role_code="inventory_admin", status=True)
        for code in [
            "inventory.view",
            "inventory.inbound",
            "inventory.outbound",
            "inventory.check",
            "inventory.update",
        ]:
            perm = PermissionEntry.objects.create(
                permission_name=code,
                permission_code=code,
                permission_type=PermissionEntry.TYPE_API,
            )
            cls.role.permission_entries.add(perm)

        cls.user = cls.user_model.objects.create_user(
            username="inv_admin",
            password="inv123456",
            role=cls.role,
            is_active=True,
        )

        cls.herb = Herb.objects.create(
            herb_code="H900",
            herb_name="测试药材",
            category="测试类",
            unit="kg",
            status=Herb.STATUS_ENABLED,
        )
        cls.stock = InventoryStock.objects.create(
            herb=cls.herb,
            current_quantity=Decimal("5.00"),
            safe_quantity=Decimal("4.00"),
            unit="kg",
            stock_status=InventoryStock.STATUS_NORMAL,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_inbound_and_outbound_record(self):
        inbound_resp = self.client.post(
            "/api/inventory/inbound/",
            {"herb_id": self.herb.id, "quantity": "10.00", "remark": "test inbound"},
            format="json",
        )
        self.assertEqual(inbound_resp.status_code, 201)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_quantity, Decimal("15.00"))

        outbound_resp = self.client.post(
            "/api/inventory/outbound/",
            {"herb_id": self.herb.id, "quantity": "3.00", "remark": "test outbound"},
            format="json",
        )
        self.assertEqual(outbound_resp.status_code, 201)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_quantity, Decimal("12.00"))

        self.assertEqual(InventoryRecord.objects.filter(herb=self.herb).count(), 2)

    def test_outbound_insufficient_returns_formatted_error(self):
        response = self.client.post(
            "/api/inventory/outbound/",
            {"herb_id": self.herb.id, "quantity": "100.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("code", response.data)
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_invalid_herb_returns_400_not_500(self):
        response = self.client.post(
            "/api/inventory/inbound/",
            {"herb_id": 999999, "quantity": "1.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("code", response.data)
        self.assertIn("errors", response.data)

    def test_warning_trigger_when_quantity_below_safe(self):
        response = self.client.post(
            "/api/inventory/outbound/",
            {"herb_id": self.herb.id, "quantity": "2.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_quantity, Decimal("3.00"))
        self.assertEqual(self.stock.stock_status, InventoryStock.STATUS_LOW)
        self.assertTrue(
            InventoryWarning.objects.filter(
                herb=self.herb, warning_status=InventoryWarning.STATUS_ACTIVE
            ).exists()
        )
