from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class LoginTokenCreateSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["refresh_token"] = str(refresh)
        data["access_token"] = str(refresh.access_token)
        data["refresh_expires_in"] = int(refresh.lifetime.total_seconds())
        data["access_expires_in"] = int(refresh.access_token.lifetime.total_seconds())
        data["token_type"] = "bearer"

        return data


class LoginTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh_token"])

        data = {"access_token": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh_token"] = str(refresh)
        data["refresh_expires_in"] = int(refresh.lifetime.total_seconds())
        data["access_expires_in"] = int(refresh.access_token.lifetime.total_seconds())
        data["token_type"] = "bearer"

        return data


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "email",
        )


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "email",
        )

    def create(self, validated_data):
        instance = super().create(validated_data=validated_data)
        instance.set_password(settings.DEFAULT_PASS)
        instance.save(update_fields=["password"])
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "is_superuser",
            "email",
        )
