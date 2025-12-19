"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# 导入你的 WebSocket 路由（如果有）
# from yourapp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # 如果有 WebSocket 支持
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(your_app.routing.websocket_urlpatterns)
    # ),
})
