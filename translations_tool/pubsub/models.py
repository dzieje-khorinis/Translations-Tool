import uuid

from django.conf import settings
from django.db import models
from django.db.models.fields import UUIDField
from django.utils import timezone

from translations_tool.pubsub.managers import ActiveWebSocketTickerManager
from translations_tool.pubsub.querysets import WebSocketTicketQuerySet


class WebSocketTicket(models.Model):
    uuid = UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expiration_datetime = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()

    objects = WebSocketTicketQuerySet.as_manager()
    active_objects = ActiveWebSocketTickerManager()

    def __str__(self):
        return f"{self.uuid} {self.ip_address}"

    def is_valid(self, ip_address):
        return not self.used and timezone.now() < self.expiration_datetime and ip_address == self.ip_address
