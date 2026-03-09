from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import PermissionEntry, Role
from herbs.models import Herb
from inventory.models import InventoryStock


class IntegrationFlowTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.role = Role.objects.create(role_name="集成测试角色", role_code="integrator", status=True)
        for code in [
            "dashboard.view",
            "herb.view",
            "herb.create",
            "inventory.view",
            "inventory.inbound",
            "inventory.outbound",
        ]:
            perm = PermissionEntry.objects.create(
                permission_name=code,
                permission_code=code,
                permission_type=PermissionEntry.TYPE_API,
            )
            cls.role.permission_entries.add(perm)
        cls.user = cls.user_model.objects.create_user(
            username="flow_user",
            password="flow123456",
            role=cls.role,
            is_active=True,
        )

    def test_api_integration_flow(self):
        api_client = APIClient()
        jwt_resp = api_client.post(
            "/api/auth/login/",
            {"username": "flow_user", "password": "flow123456"},
            format="json",
        )
        self.assertEqual(jwt_resp.status_code, 200)
        token = jwt_resp.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        access_resp = api_client.get("/api/auth/access/")
        self.assertEqual(access_resp.status_code, 200)
        self.assertIn("menu", access_resp.data)
        self.assertIn("permissions", access_resp.data)

        herb_resp = api_client.post(
            "/api/herbs/",
            {
                "herb_code": "HINT1",
                "herb_name": "集成测试药材",
                "category": "测试类",
                "unit": "kg",
                "status": "enabled",
            },
            format="json",
        )
        self.assertEqual(herb_resp.status_code, 201)
        herb_id = herb_resp.data["id"]

        inbound_resp = api_client.post(
            "/api/inventory/inbound/",
            {"herb_id": herb_id, "quantity": "6.00"},
            format="json",
        )
        self.assertEqual(inbound_resp.status_code, 201)

        herb = Herb.objects.get(pk=herb_id)
        stock = InventoryStock.objects.get(herb=herb)
        self.assertEqual(stock.current_quantity, Decimal("6.00"))
