from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from translations_tool.translations.api.views import (
    TranslationGroupViewSet,
    TranslationViewSet,
)
from translations_tool.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("groups", TranslationGroupViewSet)
router.register("translations", TranslationViewSet)


app_name = "api"
urlpatterns = router.urls
