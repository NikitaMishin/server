from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
#url(r'^ws/chat/(?P<label>[^/]+)$', consumers.ChatConsumer)
    url(r'^ws/chat/$', consumers.MultiChatConsumer)
]
