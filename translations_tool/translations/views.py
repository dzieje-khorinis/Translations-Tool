import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from ratelimit.decorators import ratelimit

from .models import Translation, TranslationGroup


@login_required
def index_view(request):
    lang = request.GET.get("lang", settings.LANGUAGE_CODE)

    ctx = {
        "languages": request.user.get_languages(),
        "lang": lang,
    }
    return render(request, "translations/index.html", context=ctx)


@login_required
def translation_tree_view(request):
    node_id = request.GET.get("node")

    lang_code = request.user.get_translation_language(lang_code=request.GET.get("lang"))

    if node_id:
        translation_groups = TranslationGroup.objects.filter(parent_id=node_id)
        translations = Translation.objects.filter(parent_id=node_id)
    else:
        translation_groups = TranslationGroup.objects.filter(parent__isnull=True)
        translations = Translation.objects.filter(parent__isnull=True)

    translation_groups = translation_groups.order_by("order_index")
    translations = translations.order_by("order_index")

    data = [
        {
            "id": group.id,
            "name": group.name,
            "type": "group",
            "load_on_demand": True,
        }
        for group in translation_groups
    ]

    data.extend(
        [
            {
                "id": translation.id,
                "name": translation.key,
                "type": "translation",
                "status": getattr(translation, f"state_{lang_code}"),
            }
            for translation in translations
        ]
    )

    return JsonResponse(data=data, safe=False)


@login_required
def translation_details_view(request):
    lang = request.user.get_translation_language(lang_code=request.GET.get("lang"))
    statuses = dict(Translation.STATUS)

    translation = get_object_or_404(Translation, id=request.GET.get("node_id"))
    state = getattr(translation, f"state_{lang}")
    ctx = {
        "translation": translation,
        "state": state,
        "state_display": statuses[state],
        "read_languages": settings.LANGUAGES,
        "write_languages": request.user.get_languages(),
        "lang": lang,
        "full_value": mark_safe(json.dumps(translation.get_full_value(), indent=4, ensure_ascii=False)),
        "full_state": mark_safe(json.dumps(translation.get_full_state(), indent=4, ensure_ascii=False)),
    }
    return render(request, "translations/translation_details.html", context=ctx)


@login_required
def translation_group_details_view(request):
    lang = request.user.get_translation_language(lang_code=request.GET.get("lang"))

    group = get_object_or_404(TranslationGroup, id=request.GET.get("node_id"))

    subgroups = TranslationGroup.objects.filter(
        Q(parent=group) | Q(parent__parent=group) | Q(parent__parent__parent=group)
    )
    groups_ids = set(subgroups.values_list("id", flat=True)) | {group.id}
    translations = Translation.objects.filter(parent_id__in=groups_ids)
    print("groups_ids", groups_ids)
    print("translations", translations)
    print("count", translations.count())

    states_counts = translations.values(state=F(f"state_{lang}")).annotate(total=Count("state")).order_by("total")
    print("states_counts", states_counts)

    ctx = {
        "group": group,
        "states_counts": states_counts,
        "lang": lang,
    }
    return render(request, "translations/translation_group_details.html", context=ctx)


@ratelimit(key="ip", rate="10/m", block=True)
@csrf_exempt
@login_required
def save_translation_view(request):
    data = {}
    if request.method == "POST":
        value = request.POST["value"]
        state = request.POST["state"].split("-")[-1]
        language = request.POST["language"]
        translation_id = request.POST["translation_id"]

        data = {
            "value": value,
            "state": state,
            "language": language,
            "translation_id": translation_id,
            "message": _("Successfully saved translation."),
            "status": "success",
        }

        translation = Translation.objects.get(id=translation_id)
        setattr(translation, f"value_{language}", value)
        setattr(translation, f"state_{language}", state)
        translation.save()
        print(data)
    return JsonResponse(data, safe=False)


def ratelimited_error(request, exception):
    # or other types:
    return JsonResponse(
        {
            "error": "ratelimited",
            "message": _("Too many requests. Please wait."),
            "status": "error",
        },
        status=429,
    )


class TranslationListJson(BaseDatatableView):
    model = Translation
    columns = ["key"]
    order_columns = ["key"]
    max_display_length = 500

    def get_columns(self):
        request = self.request
        lang = request.user.get_translation_language(lang_code=request.GET.get("lang"))
        print("get_columns.lang", lang)
        columns = super().get_columns() + [f"value_{lang}", f"state_{lang}"]
        print(columns)
        return columns

    def get_order_columns(self):
        request = self.request
        lang = request.user.get_translation_language(lang_code=request.GET.get("lang"))
        print("get_order_columns.lang", lang)
        columns = super().get_order_columns() + [f"value_{lang}", f"state_{lang}"]
        print(columns)
        return columns

    def get_initial_queryset(self):
        qs = super().get_initial_queryset()
        group_id = self.request.GET.get("group")
        if not group_id:
            return qs

        group = get_object_or_404(TranslationGroup, id=group_id)
        subgroups = TranslationGroup.objects.filter(
            Q(parent=group) | Q(parent__parent=group) | Q(parent__parent__parent=group)
        )
        groups_ids = set(subgroups.values_list("id", flat=True)) | {group.id}
        return qs.filter(parent_id__in=groups_ids)
