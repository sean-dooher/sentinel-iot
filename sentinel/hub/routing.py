from channels import route
from channels.generic.websockets import WebsocketDemultiplexer
from .models import Hub
from channels.routing import route_class
from .consumers import ws_add, ws_disconnect, ws_message
from .bindings import LeafBinding, ConditionBinding, DatastoreBinding


class APIDemultiplexer(WebsocketDemultiplexer):
    http_user = True
    consumers = {
      'leaves': LeafBinding.consumer,
      'datastores': DatastoreBinding.consumer,
      'conditions': ConditionBinding.consumer
    }

    def connect(self, message, **kwargs):
        hub = Hub.objects.filter(id=kwargs['id'])
        if not hub.exists() or not self.message.user.has_perm('view_hub', hub.first()):
            return message.reply_channel.send({"accept": False})
        return super().connect(message, **kwargs)


# top level routing for websockets
websocket_routing = [
    route("websocket.connect", ws_add, path=r"^(?P<id>[^/]+)$"),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
]


client_routing = [
    route_class(APIDemultiplexer, path=r"^(?P<id>[^/]+)$")
]
