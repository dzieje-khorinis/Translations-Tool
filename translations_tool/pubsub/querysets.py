from django.db import models
from django.utils import timezone


class WebSocketTicketQuerySet(models.QuerySet):
    def active(self):
        return self.filter(used=False, expiration_datetime__gt=timezone.now())
