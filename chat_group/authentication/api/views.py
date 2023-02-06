from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    LoginTokenCreateSerializer,
    LoginTokenRefreshSerializer,
    GetUserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ["get", "post", "patch"]
    serializer_get = GetUserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "username"

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return GetUserSerializer
        if self.request.method.lower() == "post":
            return CreateUserSerializer
        if self.request.method.lower() == "patch":
            return UpdateUserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not request.user.is_superuser:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="Only superuser can create the New Users",
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.serializer_get(instance).data
        return Response(data=response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        if not request.user.is_superuser:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="Only superuser can update the Users",
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.serializer_get(instance).data
        return Response(data=response_data, status=status.HTTP_200_OK)


class LoginTokenCreateView(TokenObtainPairView):
    serializer_class = LoginTokenCreateSerializer


class LoginTokenRefreshView(TokenRefreshView):
    serializer_class = LoginTokenRefreshSerializer
