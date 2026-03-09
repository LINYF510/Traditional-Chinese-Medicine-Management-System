from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from accounts.api import AccessAPIView, PermissionEntryViewSet, ProfileAPIView, RoleViewSet, UserViewSet
from accounts.jwt_api import JWTLoginAPIView, JWTRefreshAPIView
from formulas.api import FormulaViewSet
from herbs.api import HerbViewSet
from inventory.api import (
    InventoryCheckAPIView,
    InventoryInboundAPIView,
    InventoryOutboundAPIView,
    InventoryRecordViewSet,
    InventoryStockViewSet,
    InventoryWarningViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("roles", RoleViewSet)
router.register("permissions", PermissionEntryViewSet)
router.register("herbs", HerbViewSet)
router.register("formulas", FormulaViewSet)
router.register("inventory/stocks", InventoryStockViewSet, basename="inventory-stock")
router.register("inventory/records", InventoryRecordViewSet, basename="inventory-record")
router.register("inventory/warnings", InventoryWarningViewSet, basename="inventory-warning")

urlpatterns = [
    path("auth/login/", JWTLoginAPIView.as_view(), name="api-auth-login"),
    path("auth/refresh/", JWTRefreshAPIView.as_view(), name="api-auth-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="api-auth-verify"),
    path("", include(router.urls)),
    path("auth/profile/", ProfileAPIView.as_view(), name="api-profile"),
    path("auth/access/", AccessAPIView.as_view(), name="api-access"),
    path("inventory/inbound/", InventoryInboundAPIView.as_view(), name="api-inventory-inbound"),
    path("inventory/outbound/", InventoryOutboundAPIView.as_view(), name="api-inventory-outbound"),
    path("inventory/check/", InventoryCheckAPIView.as_view(), name="api-inventory-check"),
]
