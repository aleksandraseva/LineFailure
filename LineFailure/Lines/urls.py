from django.urls import path
from .views import connections, debug, lines, routes

urlpatterns = [
    path("", connections.show_connections, name="show_connections"),
    path("debug", debug.debug_parser, name="debug_parser"),
    path("lines", lines.connections_view, name="connections_view"),
    path("routes", routes.routes_view, name="routes_view"),
]
