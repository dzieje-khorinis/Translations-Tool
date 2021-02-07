from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .views import TranslationListJson

app_name = "translations"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("translations/", views.translations, name="translations"),
    path("translations_json/", login_required(views.TranslationsJson.as_view()), name="translations_json"),
    path("tree/", views.translation_tree_view, name="tree"),
    path("translation_details/", views.translation_details_view, name="translation_details"),
    path("translation_group_details/", views.translation_group_details_view, name="translation_group_details"),
    path("save_translation/", views.save_translation_view, name="save_translation"),
    path("translation_list/", login_required(TranslationListJson.as_view()), name="translation_list_json"),
    path("user_list/", views.user_list, name="user_list"),
    # path("create_user/", views.UserCreateView.as_view(), name="create_user"),
    path("user_activation/<int:user_id>/<int:activate>", views.user_activation, name="user_activation"),
]
