from channels.routing import route
from hub.consumers import ws_add, ws_message, ws_disconnect

channel_routing = [
    route("websocket.connect", ws_add, path=r"^/(?P<group>[a-zA-Z0-9\-]+)/$"),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
]
