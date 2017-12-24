from channels import route
from .consumers import *

# top level routing for websockets
websocket_routing = [
    route("websocket.connect", ws_add),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect)
]