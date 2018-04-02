from  channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
from chat.websocket_auth import JWTAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': JWTAuthMiddleware(
        # 'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})
