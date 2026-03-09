from rest_framework import permissions, serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_permissions import RBACPermission
from .models import PermissionEntry, Role, User
from .navigation import build_visible_menu


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "role_name", "role_code", "description", "status"]


class PermissionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionEntry
        fields = ["id", "permission_name", "permission_code", "permission_type", "path", "description"]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.role_name", read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "real_name",
            "email",
            "phone",
            "gender",
            "role",
            "role_name",
            "is_active",
            "is_staff",
            "last_login",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    permission_code_map = {"GET": "role.view"}


class PermissionEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PermissionEntry.objects.all()
    serializer_class = PermissionEntrySerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    permission_code_map = {"GET": "permission.view"}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("role").all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    search_fields = ["username", "real_name", "email", "phone"]
    filterset_fields = ["role", "is_active", "is_staff"]
    permission_code_map = {
        "list": "user.view",
        "retrieve": "user.view",
        "create": "user.create",
        "update": "user.update",
        "partial_update": "user.update",
        "destroy": "user.delete",
    }


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AccessAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "permissions": sorted(request.user.get_permission_codes()),
                "menu": build_visible_menu(request.user),
            }
        )
