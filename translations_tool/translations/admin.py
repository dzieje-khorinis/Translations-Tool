import json

from django.contrib import admin
from django.forms import MediaDefiningClass
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from simple_history.admin import SimpleHistoryAdmin
from translated_fields import TranslatedFieldAdmin

from .models import Translation, TranslationGroup


def flatten(list_of_lists):
    return [y for x in list_of_lists for y in x]


class ChangedFieldMixin:
    def changed(self, obj):
        prev = obj.prev_record
        before = {}
        after = {}
        if prev:
            delta = obj.diff_against(prev)
            for change in delta.changes:
                before[change.field] = change.old
                after[change.field] = change.new

        result = ""
        if before and after:
            result += json.dumps(before, indent=4, ensure_ascii=False)
            result += "\n" + "-" * 30 + "\n"
            result += json.dumps(after, indent=4, ensure_ascii=False)

        result = f'<textarea disabled style="width: 400px; height: 200px;">{result}</textarea>'
        return mark_safe(result)


class ColoredStateMeta(MediaDefiningClass):
    STATUS_TO_COLOR = {
        Translation.NEW: "blue",
        Translation.TODO: "yellow",
        Translation.READY_TO_REVIEW: "orange",
        Translation.NEEDS_WORK: "red",
        Translation.ACCEPTED: "green",
    }

    def __new__(cls, name, bases, dct):
        list_display = []
        for attr in dct["list_display"]:
            if attr.startswith("state"):
                state, lang = attr.split("_")

                def lang_wrapper(lang):
                    def get_state(self, value):
                        state_value = getattr(value, f"state_{lang}")
                        color = ColoredStateMeta.STATUS_TO_COLOR.get(state_value, "black")
                        return mark_safe(f'<span style="color: {color};">{state_value}</span>')

                    return get_state

                get_state = lang_wrapper(lang)
                get_state.short_description = _("State") + f" [{lang.upper()}]"

                list_display.append(f"get_{attr}")
                dct[f"get_{attr}"] = get_state
            else:
                list_display.append(attr)
        dct["list_display"] = list_display

        return super().__new__(cls, name, bases, dct)


class TranslationGroupAdmin(ChangedFieldMixin, TranslatedFieldAdmin, SimpleHistoryAdmin):
    history_list_display = ["changed"]
    list_display = ["edit", "parent"] + TranslationGroup.name.fields

    def edit(self, value):
        return "Edit"


class TranslationAdmin(ChangedFieldMixin, TranslatedFieldAdmin, SimpleHistoryAdmin, metaclass=ColoredStateMeta):
    history_list_display = ["changed"]
    list_display = ["key"] + flatten(zip(Translation.value.fields, Translation.state.fields))
    search_fields = list_display


admin.site.register(Translation, TranslationAdmin)
admin.site.register(TranslationGroup, TranslationGroupAdmin)
