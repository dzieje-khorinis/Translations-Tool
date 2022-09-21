import requests
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from rest_framework.renderers import JSONRenderer

from translations_tool.translations.api import serializers
from translations_tool.users.api import serializers as user_serializers

CONNECT_SERIALIZERS = [
    serializers.TranslationSerializer,
    user_serializers.UserSerializer,
]

CONNECTED_MODELS_WITH_SERIALIZERS = {serializer.Meta.model: serializer for serializer in CONNECT_SERIALIZERS}


def add_history_language(sender, **kwargs):
    from translations_tool.translations.models import LanguageHistoricalModel

    if not issubclass(sender, LanguageHistoricalModel):
        return

    history_instance = kwargs["history_instance"]

    if not history_instance.prev_record:
        return

    changed_fields = history_instance.diff_against(history_instance.prev_record).changed_fields
    changed_fields_languages = set(field.split("_")[-1] for field in changed_fields)
    if len(changed_fields_languages) == 1:
        history_instance.language = next(iter(changed_fields_languages))


def send_post_save_data_to_nchan(sender, instance, created=False, **kwargs):
    print("sender", sender)
    print("instance", instance)
    print("kwargs", kwargs)

    if hasattr(instance, "tracker"):
        print("changed", instance.tracker.changed())

    serializer = CONNECTED_MODELS_WITH_SERIALIZERS[instance.__class__](instance)
    data = serializer.data
    data["META"] = {
        "class": instance.__class__.__name__.upper(),
        "action": "CREATE" if created else "UPDATE",
    }
    print(data)
    if settings.NCHAN_PUB_ADDRESS:
        requests.post(
            f"{settings.NCHAN_PUB_ADDRESS}/pub",
            data=JSONRenderer().render(data),
            timeout=3,
        )


def send_pre_delete_data_to_nchan(sender, instance, **kwargs):
    data = {
        "id": instance.id,
        "META": {
            "class": instance.__class__.__name__.upper(),
            "action": "DELETE",
        },
    }
    print(data)
    if settings.NCHAN_PUB_ADDRESS:
        requests.post(
            f"{settings.NCHAN_PUB_ADDRESS}/pub",
            data=JSONRenderer().render(data),
            timeout=3,
        )


for serializer in CONNECT_SERIALIZERS:
    post_save.connect(send_post_save_data_to_nchan, sender=serializer.Meta.model)
    pre_delete.connect(send_pre_delete_data_to_nchan, sender=serializer.Meta.model)
