from django.conf.urls import url

from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    UserViewSet,
    LoginTokenCreateView,
    LoginTokenRefreshView,
)


class CustomApiRouter(SimpleRouter):
    """Default router for Mel rest api

    Makes trailing slash optional.
    """

    def __init__(self):
        self.trailing_slash = "/?"
        super(SimpleRouter, self).__init__()


router = CustomApiRouter()
router.register(r"users", UserViewSet, basename="users")

json_url_patterns = [
    url(r"^login/", LoginTokenCreateView.as_view()),
    url(r"token/", LoginTokenRefreshView.as_view()),
]
router_urls = router.urls
urlpatterns = router_urls + json_url_patterns
urlpatterns = format_suffix_patterns(urlpatterns, allowed=["raw"])
