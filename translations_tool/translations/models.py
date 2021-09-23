from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from translated_fields import TranslatedField


class Directory(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)
    leaf = models.BooleanField(default=False)

    def __str__(self):
        return f"Directory: {self.path}"


class TranslationGroup(models.Model):
    name = TranslatedField(models.CharField(max_length=255, blank=True))
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)

    history = HistoricalRecords()

    order_index = models.IntegerField(default=0)

    def __str__(self):
        return f"TranslationGroup: {self.name}"


class Translation(models.Model):
    NEW = "NEW"
    TODO = "TODO"
    READY_TO_REVIEW = "READY_TO_REVIEW"
    NEEDS_WORK = "NEEDS_WORK"
    ACCEPTED = "ACCEPTED"

    STATUS = [
        (NEW, _("New")),
        (TODO, _("To do")),
        (READY_TO_REVIEW, _("Ready to review")),
        (NEEDS_WORK, _("Needs work")),
        (ACCEPTED, _("Accepted")),
    ]

    key = models.TextField(max_length=2000, db_index=True)
    parent = models.ForeignKey(TranslationGroup, on_delete=models.SET_NULL, blank=True, null=True)

    value = TranslatedField(models.TextField(max_length=2000, blank=True))
    state = TranslatedField(models.CharField(max_length=255, choices=STATUS, default=NEW))

    history = HistoricalRecords()

    order_index = models.IntegerField(default=0)

    # metadata
    file = models.CharField(max_length=1000, blank=True, db_index=True)
    line = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Translation: {self.key}"

    def get_full_value(self):
        return {lang_code: getattr(self, f"value_{lang_code}") for lang_code, lang_name in settings.LANGUAGES}

    def get_full_state(self):
        return {lang_code: getattr(self, f"state_{lang_code}") for lang_code, lang_name in settings.LANGUAGES}
