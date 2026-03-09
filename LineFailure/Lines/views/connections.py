from django.shortcuts import render
from Lines.models.Connection import Connection
from Lines.management.commands import parseExcel


def show_connections(request):
    parseExcel.find_connection()
    connections = Connection.objects.all()
    return render(request, "connections.html", {"connections": connections})
