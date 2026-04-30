import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bookshelf.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({ # HTTP인지 Websocket인지 확인
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(   # 허용된 호스트의 요청인지
        AuthMiddlewareStack(    # 소켓 연결 중에도 유저 정보를 사용할 수 있게함.
            URLRouter(chat.routing.websocket_urlpatterns) # 웹소켓 정보를 인자에 연결
        )
    ),
})
