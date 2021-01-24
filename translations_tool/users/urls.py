from django.urls import path

from translations_tool.users.views import (
    UserCreateView,
    change_password_view,
    user_detail_view,
    user_profile_view,
    user_redirect_view,
    user_update_view,
)

app_name = "users"
urlpatterns = [
    path("profile/", user_profile_view, name="profile"),
    path("change_password/", change_password_view, name="change_password"),
    path("create_user/", UserCreateView.as_view(), name="create_user"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
