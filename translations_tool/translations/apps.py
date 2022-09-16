from django.apps import AppConfig
from simple_history.signals import pre_create_historical_record

from translations_tool.translations.signals import add_history_language


class TranslationsConfig(AppConfig):
    name = "translations_tool.translations"

    def ready(self) -> None:
        pre_create_historical_record.connect(
            add_history_language,
        )
