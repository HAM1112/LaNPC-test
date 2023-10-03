from . import consumers
from django.urls import path

websocket_urlpatterns = [
    path('user/chat/<int:game_id>/', consumers.ChatConsumer.as_asgi()), 
]