from django.urls import path

from . import views

app_name = "translations"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("tree/", views.translation_tree_view, name="tree"),
    path("translation_details/", views.translation_details_view, name="translation_details"),
    path("translation_group_details/", views.translation_group_details_view, name="translation_group_details"),
    path("save_translation/", views.save_translation_view, name="save_translation"),
]
