from django.urls import re_path
from channels.db import database_sync_to_async
from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer

from .consumers import LeafConsumer
from .bindings import LeafBinding, ConditionBinding, DatastoreBinding
from .models import Hub


class APIDemultiplexer(AsyncJsonWebsocketDemultiplexer):
    http_user = True
    applications = {
      'leaves': LeafBinding,
      'datastores': DatastoreBinding,
      'conditions': ConditionBinding
    }

    async def websocket_connect(self, message):
        hub_id = self.scope['url_route']['kwargs']['id']
        hub = await database_sync_to_async(Hub.objects.filter)(id=hub_id)
        if not hub.exists() or not self.scope['user'].has_perm('view_hub', hub.first()):
            return await self.close()
        return await super().websocket_connect(message)


# top level routing for websockets
websocket_routing = [
    re_path(r"^hub/(?P<id>[^/]+)$", LeafConsumer),
    re_path(r"^client/(?P<id>[^/]+)$", APIDemultiplexer)
]