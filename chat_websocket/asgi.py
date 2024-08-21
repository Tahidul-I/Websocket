import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from apps.chatbox import routing as chatbox_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_websocket.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chatbox_routing.websocket_urlpatterns
            )
        )
    ),
})
