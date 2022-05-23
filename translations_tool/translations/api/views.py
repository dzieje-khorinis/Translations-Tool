from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import Directory, Translation, TranslationGroup
from .serializers import (
    DirectorySerializer,
    HistoryPaginationSerializer,
    HistoryRecordSerializer,
    TranslationGroupSerializer,
    TranslationPaginationSerializer,
    TranslationSaveSerializer,
    TranslationSerializer,
)


class DirectoryViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = DirectorySerializer
    queryset = Directory.objects.all()

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def search(self, request):
        search = self.request.GET.get("search")
        qs = super().get_queryset()
        if search:
            qs = qs.filter(path__icontains=search)
        qs = qs.order_by("path")[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @method_decorator(cache_page(60 * 60 * 2))
    @action(detail=False)
    def root(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs.filter(parent=None).first(), many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @method_decorator(cache_page(60 * 60 * 2))
    @action(detail=True)
    def children(self, request, pk=None):
        parent = self.get_object()
        serializer = self.get_serializer(parent.children.order_by("name"), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class TranslationGroupViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = TranslationGroupSerializer
    queryset = TranslationGroup.objects.all()
    lookup_field = "name"

    def get_queryset(self):
        language = self.request.GET.get("language") or "en"
        search = self.request.GET.get("search")
        qs = super().get_queryset()
        field_name = f"name_{language}"
        if search:
            qs = qs.filter(**{f"{field_name}__icontains": search})
        return qs.order_by(f"{field_name}")[:10]


class HistoryRecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 50


class TranslationsHistoryViewSet(ListModelMixin, GenericViewSet):
    serializer_class = HistoryRecordSerializer
    pagination_class = HistoryRecordPagination
    queryset = Translation.history.order_by("-history_date").select_related("history_user")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        serializer = HistoryPaginationSerializer(data=request.GET, context={"request": request})
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        if "translation_id" in filters:
            qs = qs.filter(id=filters["translation_id"])

        if "user_id" in filters:
            qs = qs.filter(history_user_id=filters["user_id"])

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


class TranslationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 50


class TranslationViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = TranslationSerializer
    pagination_class = TranslationPagination
    queryset = Translation.objects.order_by("id")

    def list(self, request, *args, **kwargs):
        def prepare_aggregations(qs):
            state_fieldname = f"state_{data_language}"
            qs = qs.values(state_fieldname).annotate(dcount=Count(state_fieldname)).order_by()
            statuses = dict(Translation.STATUS)
            aggregations = statuses.fromkeys(statuses, 0)
            for row in qs:
                state = row[state_fieldname]
                count = row["dcount"]
                aggregations[state] = count
            return aggregations

        serializer = TranslationPaginationSerializer(data=request.GET, context={"request": request})
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        qs = self.get_queryset()

        data_language = filters["dataLanguage"] or "en"
        total_aggregations = prepare_aggregations(qs)

        if filters["path"]:
            qs = qs.filter(file__istartswith=filters["path"])

        if filters["states"]:
            qs = qs.filter(**{f"state_{data_language}__in": filters["states"]})

        if filters["state"]:
            qs = qs.filter(**{f"state_{data_language}": filters["state"]})

        if filters["order_by"]:
            qs = qs.order_by(f"{'-' if filters['order_direction'] == 'desc' else ''}{filters['order_by']}")

        if filters["group"]:
            qs = qs.filter(**{f"parent__name_{data_language}": filters["group"]})

        if filters["searchTerm"]:
            qs = qs.filter(
                Q(**{"key__icontains": filters["searchTerm"]})
                | Q(**{f"value_{data_language}__icontains": filters["searchTerm"]})
            )

        current_aggregations = prepare_aggregations(qs)
        qs = self.paginate_queryset(qs)
        paginator = self.paginator.page.paginator
        serializer = self.get_serializer(qs, many=True)
        data = {
            "page": self.paginator.page.number,
            "per_page": paginator.per_page,
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "aggregations": {key: [value, total_aggregations[key]] for key, value in current_aggregations.items()},
            "data": serializer.data,
        }

        return Response(status=status.HTTP_200_OK, data=data)

    @action(detail=False, methods=["POST"])
    def save(self, request):
        serializer = TranslationSaveSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        try:
            translation = Translation.objects.get(id=data["translation_id"])
        except Translation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        language = data["language"]
        value = data["text"]
        state = data["state"]
        setattr(translation, f"value_{language}", value)
        setattr(translation, f"state_{language}", state)
        translation.save()
        return Response(status=status.HTTP_200_OK, data=serializer.validated_data)
