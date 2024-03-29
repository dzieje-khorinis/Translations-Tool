from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter, SimpleRouter

from translations_tool.pubsub.views import IssueWebSocketTicket, UserAuthCheckView
from translations_tool.translations.api.views import (
    DirectoryViewSet,
    TranslationGroupViewSet,
    TranslationsHistoryViewSet,
    TranslationViewSet,
)
from translations_tool.users.api.views import (
    ChangePasswordView,
    ObtainAuthTokenView,
    UserViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("groups", TranslationGroupViewSet)
router.register("translations", TranslationViewSet)
router.register("translations_history", TranslationsHistoryViewSet)
router.register("directories", DirectoryViewSet)


urlpatterns = [
    path("", include("translations_tool.translations.urls", namespace="translations")),
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("translations_tool.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("i18n/", include("django.conf.urls.i18n")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    path("api/", include(router.urls)),
    path("api/auth-token/", ObtainAuthTokenView.as_view()),
    path("api/change_password/", ChangePasswordView.as_view()),
    path("api/auth-check/", UserAuthCheckView.as_view()),  # used internally by nchan to validate websocket connection
    path("api/issue-web-socket-ticket/", IssueWebSocketTicket.as_view()),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
