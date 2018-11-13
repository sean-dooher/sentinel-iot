from .models import Hub
from django.urls import re_path
from .consumers import LeafConsumer
# from .bindings import LeafBinding, ConditionBinding, DatastoreBinding

# TODO: investigate websocket client replacement framework

# class APIDemultiplexer(WebsocketDemultiplexer):
#     http_user = True
#     consumers = {
#       'leaves': LeafBinding.consumer,
#       'datastores': DatastoreBinding.consumer,
#       'conditions': ConditionBinding.consumer
#     }

#     def connect(self, message, **kwargs):
#         hub = Hub.objects.filter(id=kwargs['id'])
#         if not hub.exists() or not self.message.user.has_perm('view_hub', hub.first()):
#             return message.reply_channel.send({"accept": False})
#         return super().connect(message, **kwargs)


# top level routing for websockets
websocket_routing = [
    re_path(r"^hub/(?P<id>[^/]+)$", LeafConsumer),
    # re_path(r"^client/(?P<id>[^/]+)$", ClientConsumer)
]