from django.urls import path
from .views import connections, debug

urlpatterns = [
    path("", connections.show_connections, name="show_connections"),
    path("debug", debug.debug_parser, name="debug_parser"),
]
