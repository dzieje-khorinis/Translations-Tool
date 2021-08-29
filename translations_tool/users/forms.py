from django.conf import settings
from django.contrib.auth import forms as admin_forms
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from translations_tool.users.models import User


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(admin_forms.UserCreationForm):

    error_message = admin_forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class UserCreationFormWithRoles(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "role", "role_related_language")
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        user = request.user
        roles = dict(User.ROLE)
        languages = dict(settings.LANGUAGES)
        super().__init__(*args, **kwargs)

        role_choices = []
        language_choices = []
        if user.role == User.COORDINATOR:
            role_choices.extend(
                [
                    (User.TRANSLATOR, roles[User.TRANSLATOR]),
                ]
            )
            language_choices.extend(
                [
                    (user.role_related_language, languages[user.role_related_language]),
                ]
            )
        elif user.role == User.ADMIN:
            role_choices.extend(
                [
                    (User.COORDINATOR, roles[User.COORDINATOR]),
                    (User.TRANSLATOR, roles[User.TRANSLATOR]),
                ]
            )
            language_choices.extend(settings.LANGUAGES)
        elif user.is_superuser:
            role_choices.extend(
                [
                    (User.COORDINATOR, roles[User.COORDINATOR]),
                    (User.TRANSLATOR, roles[User.TRANSLATOR]),
                    (User.ADMIN, roles[User.ADMIN]),
                ]
            )
            language_choices.append(("", "---------"))
            language_choices.extend(settings.LANGUAGES)

        self.fields["role"].choices = role_choices
        self.fields["role_related_language"].choices = language_choices
