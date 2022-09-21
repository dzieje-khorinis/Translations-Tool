from django.db import models
from django.utils import timezone


class ActiveWebSocketTickerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(used=False, expiration_datetime__gt=timezone.now())
