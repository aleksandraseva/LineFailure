from django.shortcuts import render
from Lines.models.Connection import Connection
from Lines.services import parseExcel


def show_connections(request):

    connections = Connection.objects.all()
    size = Connection.objects.count()
    return render(
        request, "connections.html", {"connections": connections, "size": size}
    )
