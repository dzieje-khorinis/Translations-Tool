from django.conf import settings
from rest_framework import serializers

from translations_tool.translations.api.fields import CommaSeparatedListField
from translations_tool.translations.models import (
    Directory,
    Translation,
    TranslationGroup,
)


class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = ["id", "name", "path", "leaf"]


class TranslationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationGroup
        fields = ["id", "name"]


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = [
            "id",
            "key",
            *[f"value_{lang}" for lang in settings.LANGUAGES_DICT],
            *[f"state_{lang}" for lang in settings.LANGUAGES_DICT],
            "file",
            "line",
            "parent",
        ]


class TranslationPaginationSerializer(serializers.Serializer):
    order_direction = serializers.CharField(max_length=128, write_only=True, default="asc")
    order_by = serializers.CharField(max_length=128, write_only=True, default="")
    per_page = serializers.IntegerField(write_only=True, default=10)
    page = serializers.IntegerField(write_only=True, default=1)
    dataLanguage = serializers.CharField(max_length=128, default="", write_only=True)
    searchTerm = serializers.CharField(max_length=128, default="", write_only=True)
    group = serializers.CharField(max_length=128, default="", write_only=True)
    state = serializers.CharField(max_length=128, default="", write_only=True)
    path = serializers.CharField(max_length=2000, default="", write_only=True)
    states = CommaSeparatedListField(max_length=128, default="", write_only=True)


class TranslationSaveSerializer(serializers.Serializer):
    translation_id = serializers.IntegerField(write_only=True, required=True)
    state = serializers.CharField(max_length=128, write_only=True, required=True)
    text = serializers.CharField(max_length=128, write_only=True, required=True)
    language = serializers.CharField(max_length=2, write_only=True, required=True)


class HistoryPaginationSerializer(serializers.Serializer):
    translation_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)


class HistoryUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class HistoryRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="history_id")
    translation_id = serializers.IntegerField(source="id")
    date = serializers.DateTimeField(source="history_date")
    user = HistoryUserSerializer(source="history_user")
    diff = serializers.SerializerMethodField()

    def get_diff(self, obj):
        prev_record = obj.prev_record
        if prev_record:
            return [change.__dict__ for change in obj.diff_against(prev_record).changes]
        return []
