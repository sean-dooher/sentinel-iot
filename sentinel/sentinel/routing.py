from channels.routing import route, include

channel_routing = [
    include("hub.routing.websocket_routing", path=r"^/hub/")
]
