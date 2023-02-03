"""
ASGI config for holla project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
#import main.urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holla.settings')

application = get_asgi_application()

#application = ProtocolTypeRouter({
#  'http': get_asgi_application(),
#  'websocket': URLRouter(
#      main.urls.websocket_urlpatterns
#    ),
#})
