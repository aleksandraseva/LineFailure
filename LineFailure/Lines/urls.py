from django.urls import path
from .views import connections

urlpatterns = [
    path("", connections.show_connections, name="show_connections"),
]
