from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import PermissionEntry, Role


class AuthAndRBACTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.admin_role = Role.objects.create(role_name="管理员", role_code="admin", status=True)
        cls.pharmacist_role = Role.objects.create(role_name="药剂师", role_code="pharmacist", status=True)

        permission_codes = [
            "dashboard.view",
            "herb.view",
            "formula.view",
            "inventory.view",
            "user.view",
            "user.create",
            "user.update",
            "user.delete",
            "role.view",
            "permission.view",
        ]
        cls.permissions = {}
        for code in permission_codes:
            cls.permissions[code] = PermissionEntry.objects.create(
                permission_name=code,
                permission_code=code,
                permission_type=PermissionEntry.TYPE_API,
            )

        cls.admin_role.permission_entries.set(PermissionEntry.objects.all())
        cls.pharmacist_role.permission_entries.set(
            [
                cls.permissions["dashboard.view"],
                cls.permissions["herb.view"],
                cls.permissions["inventory.view"],
            ]
        )

        cls.admin_user = cls.user_model.objects.create_user(
            username="admin_test",
            password="admin123456",
            role=cls.admin_role,
            is_active=True,
        )
        cls.pharmacist_user = cls.user_model.objects.create_user(
            username="pharm_test",
            password="pharm123456",
            role=cls.pharmacist_role,
            is_active=True,
        )

    def setUp(self):
        self.client = APIClient()

    def test_jwt_login_success(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "admin_test", "password": "admin123456"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_jwt_login_failure(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "admin_test", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_rbac_forbid_user_create_for_pharmacist(self):
        self.client.force_authenticate(self.pharmacist_user)
        response = self.client.post(
            "/api/users/",
            {"username": "blocked_user", "password": "blocked123", "real_name": "No Access"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_user_create_for_admin(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(
            "/api/users/",
            {
                "username": "normal_user",
                "password": "normal123456",
                "real_name": "普通用户",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        created = self.user_model.objects.get(username="normal_user")
        self.assertTrue(created.check_password("normal123456"))

    def test_access_endpoint_returns_permissions_and_menu(self):
        self.client.force_authenticate(self.pharmacist_user)
        response = self.client.get("/api/auth/access/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.data)
        self.assertIn("permissions", response.data)
        self.assertIn("menu", response.data)
        self.assertIn("herb.view", response.data["permissions"])
