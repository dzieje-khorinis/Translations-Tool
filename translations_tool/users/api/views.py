from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    ActivateUserSerializer,
    ChangePasswordSerializer,
    CreateUserSerializer,
    UserPagination,
    UserSerializer,
)

User = get_user_model()


class ObtainAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    pagination_class = UserPagination
    queryset = User.objects.all()
    lookup_field = "username"

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs = self.paginate_queryset(qs)
        paginator = self.paginator.page.paginator
        serializer = self.get_serializer(qs, many=True)
        data = {
            "page": self.paginator.page.number,
            "per_page": paginator.per_page,
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "data": serializer.data,
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def get_queryset(self, *args, **kwargs):
        return self.request.user.editable_users()

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["POST"])
    def activate(self, request):
        serializer = ActivateUserSerializer(request.user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["POST"])
    def make(self, request):
        serializer = CreateUserSerializer(request.user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, "auth_token"):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
