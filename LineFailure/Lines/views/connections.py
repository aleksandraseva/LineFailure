from django.shortcuts import render
from Lines.models.Connection import Connection
from Lines.services import parseExcel

connections = None


def show_connections(request):
    global connections
    if connections is None:
        parseExcel.find_connection()

    connections = Connection.objects.all()
    size = Connection.objects.count()
    return render(
        request, "connections.html", {"connections": connections, "size": size}
    )
