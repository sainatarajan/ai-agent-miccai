"""
ASGI config for ncbi_agent project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ncbi_agent.settings")
django.setup()

# Import after Django setup to avoid apps registry errors
from ncbi_chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
