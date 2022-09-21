import uuid
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from translations_tool.pubsub.models import WebSocketTicket


class IssueWebSocketTicket(APIView):
    http_method_names = ["post"]

    def post(self, *args, **kwargs):
        ticket, _ = WebSocketTicket.objects.update_or_create(
            user=self.request.user,
            defaults={
                "uuid": uuid.uuid4(),
                "expiration_datetime": timezone.now() + timedelta(seconds=60),
                "used": False,
                "ip_address": self.request.META.get("REMOTE_ADDR"),
            },
        )

        print("REMOTE_ADDR", self.request.META.get("REMOTE_ADDR"))
        print("HTTP_X_FORWARDED_FOR", self.request.META.get("HTTP_X_FORWARDED_FOR"))
        # ticket, _ = WebSocketTicket.objects.get_or_create(user=)
        return Response({"ticket": ticket.uuid})


class UserAuthCheckView(View):
    http_method_names = ["get"]

    def get(self, *args, **kwargs):
        headers = self.request.headers
        if "X-Original-Uri" in headers and "X-Real-Ip" in headers:
            ip_address = headers["X-Real-Ip"]
            print("ip_address", ip_address)
            ticket_uuid = parse_qs(urlparse(headers["X-Original-Uri"]).query).get("ticket")
            if ticket_uuid:
                try:
                    ticket = WebSocketTicket.active_objects.get(uuid=ticket_uuid[0])
                    ticket.used = True
                    ticket.save()
                    return HttpResponse(status=status.HTTP_200_OK)
                except WebSocketTicket.DoesNotExist:
                    pass

            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

        if self.request.user.is_authenticated:
            return HttpResponse(status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
