from channels import route
from .consumers import *

# top level routing for websockets
websocket_routing = [
    route("websocket.connect", ws_add),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect)
]

# messages are then decoded and passed through again to their handlers

hub_routing = [
    route("hub.receive", ws_handle_config, type="^CONFIG$"),
    route("hub.receive", ws_handle_status, type="^DEVICE_STATUS$"),
    route("hub.receive", ws_handle_subscribe, type="^SUBSCRIBE$"),
    route("hub.receive", ws_handle_unsubscribe, type="^UNSUBSCRIBE$"),
]