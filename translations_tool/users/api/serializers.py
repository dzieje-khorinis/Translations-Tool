from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "role_related_language", "is_active"]

        extra_kwargs = {"url": {"view_name": "api:user-detail", "lookup_field": "username"}}

    def get_role(self, obj):
        if obj.is_superuser:
            return User.ADMIN
        return obj.role


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 50


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return value

    def validate(self, data):
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError({"new_password2": _("The two password fields didn't match.")})
        password_validation.validate_password(data["new_password1"], self.context["request"].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password1"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user


class ActivateUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(write_only=True, required=True)
    activate = serializers.BooleanField(write_only=True, required=True)

    def validate_user_id(self, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User does not exist."))

    def validate(self, data):
        user = self.context["request"].user
        if not user.editable_users().filter(id=data["user_id"].id).exists():
            raise serializers.ValidationError(_("You do not have permission to perform this action!"))
        return data

    def save(self, **kwargs):
        activate = self.validated_data["activate"]
        target_user = self.validated_data["user_id"]
        target_user.is_active = activate
        target_user.save()
        return target_user


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, write_only=True, required=True)
    role = serializers.CharField(max_length=128, write_only=True, required=True)
    role_related_language = serializers.CharField(max_length=128, write_only=True, required=True)
    password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("User already exists."))
        return value

    def validate_role(self, data):
        user = self.context["request"].user
        if data not in user.lower_roles():
            raise serializers.ValidationError(_("Invalid role."))
        return data

    def validate_role_related_language(self, data):
        user = self.context["request"].user
        if not user.is_superuser and user.role == "COORDINATOR" and data != user.role_related_language:
            raise serializers.ValidationError(_("Invalid role related language."))
        return data

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": _("The two password fields didn't match.")})
        password_validation.validate_password(data["password1"], self.context["request"].user)
        return data

    def save(self, **kwargs):
        data = self.validated_data
        user = User.objects.create(
            username=data["username"],
            role=data["role"],
            role_related_language=data["role_related_language"],
        )
        user.set_password(data["password1"])
        user.save()
        return user
