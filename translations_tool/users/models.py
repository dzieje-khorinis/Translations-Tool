from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ForeignKey
from django.db.models.deletion import SET_NULL
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from translations_tool.translations.models import Translation


class User(AbstractUser):
    chief = ForeignKey("self", on_delete=SET_NULL, blank=True, null=True, related_name="subordinates")
    ADMIN = "ADMIN"
    COORDINATOR = "COORDINATOR"
    TRANSLATOR = "TRANSLATOR"
    ROLE = [
        (ADMIN, _("Admin")),
        (COORDINATOR, _("Coordinator")),
        (TRANSLATOR, _("Translator")),
    ]
    role = CharField(max_length=255, choices=ROLE, blank=True)
    role_related_language = CharField(max_length=2, choices=settings.LANGUAGES, blank=True)

    def is_admin(self):
        return self.is_superuser or self.role == User.ADMIN

    def get_languages(self):
        languages = dict(settings.LANGUAGES)
        if not self.role and not self.is_superuser:
            return []

        if self.role in (User.COORDINATOR, User.TRANSLATOR) and not self.is_superuser:
            return [(self.role_related_language, languages[self.role_related_language])]

        return settings.LANGUAGES

    def get_translation_language(self, lang_code):
        if self.role in (User.COORDINATOR, User.TRANSLATOR) and not self.is_superuser:
            return self.role_related_language
        return lang_code or settings.LANGUAGE_CODE

    def get_state_actions(self):
        actions = []

        if not self.role and not self.is_superuser:
            return actions

        actions.extend(
            [
                Translation.TODO,
                Translation.READY_TO_REVIEW,
            ]
        )
        if self.role == User.TRANSLATOR and not self.is_superuser:
            return actions

        actions.extend(
            [
                Translation.NEEDS_WORK,
                Translation.ACCEPTED,
            ]
        )

        if self.role == User.COORDINATOR and not self.is_superuser:
            return actions

        actions = [Translation.NEW] + actions
        return actions

    def get_role(self):
        if self.is_superuser:
            return _("Super Admin")

        if not self.role:
            return _("None")

        role_code_to_value = dict(User.ROLE)
        role_pretty = role_code_to_value[self.role]
        if self.role in (User.COORDINATOR, User.TRANSLATOR) and self.role_related_language:
            role_pretty = f"{role_pretty} [{self.role_related_language.upper()}]"

        return role_pretty

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
