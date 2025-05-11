from django.urls import path
from .consumers import ListingConsumer

ws_urlpatterns = [
    path('ws/listing/<id>', ListingConsumer.as_asgi()),
]
