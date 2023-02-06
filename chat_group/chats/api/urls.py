from rest_framework.routers import SimpleRouter

from .views import ChatGroupViewset, MessageViewset


class CustomApiRouter(SimpleRouter):
    """Default router for Mel rest api

    Makes trailing slash optional.
    """

    def __init__(self):
        self.trailing_slash = "/?"
        super(SimpleRouter, self).__init__()


router = CustomApiRouter()
router.register(r"chatgroups", ChatGroupViewset, basename="chatgroups")
router.register(r"messages", MessageViewset, basename="messages")

urlpatterns = router.urls
