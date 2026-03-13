from django.urls import path
from .views import connections, debug, points

urlpatterns = [
    path("", connections.show_connections, name="show_connections"),
    path("debug", debug.debug_parser, name="debug_parser"),
    path("path", points.select_items_view, name="select_items_view"),
]
