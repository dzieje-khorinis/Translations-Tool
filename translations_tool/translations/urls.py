from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .views import TranslationListJson

app_name = "translations"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("tree/", views.translation_tree_view, name="tree"),
    path("translation_details/", views.translation_details_view, name="translation_details"),
    path("translation_group_details/", views.translation_group_details_view, name="translation_group_details"),
    path("save_translation/", views.save_translation_view, name="save_translation"),
    path("translation_list/", login_required(TranslationListJson.as_view()), name="translation_list_json"),
    path("user_list/", views.user_list, name="user_list"),
    path("create_user/", views.create_user, name="create_user"),
    path("remove_user/", views.remove_user, name="remove_user"),
]
