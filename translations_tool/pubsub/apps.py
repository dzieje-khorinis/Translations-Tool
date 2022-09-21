from django.apps import AppConfig


class PubSubConfig(AppConfig):
    name = "translations_tool.pubsub"

    def ready(self):
        try:
            import translations_tool.pubsub.signals  # noqa F401
        except ImportError:
            pass
