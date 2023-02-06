from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="GroupChat API Documentation",
        default_version="v1",
        description="Welcome to the GroupChat api docs",
        terms_of_service="",
        contact=openapi.Contact(email="rishijha424@gmail.com"),
        license=openapi.License(name="Rishikesh Jha Personal"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^doc(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),  # <-- Here
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),  # <-- Here
    # path(
    #     r"api/v1/",
    #     include(("chats.api.urls", "administration"), namespace="restapi"),
    # ),
    path(r"api/v1/", include("authentication.api.urls")),
    path(r"api/v1/", include("chats.api.urls")),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
