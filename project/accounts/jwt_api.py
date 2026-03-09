from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User


class JWTUserSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.role_code", read_only=True)
    role_name = serializers.CharField(source="role.role_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "real_name",
            "email",
            "phone",
            "is_active",
            "role_code",
            "role_name",
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role.role_code if user.role else ""
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = JWTUserSerializer(self.user).data
        return data


class JWTLoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class JWTRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny]
