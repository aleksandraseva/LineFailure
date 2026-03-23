from django.shortcuts import render
from Lines.models.Service import Service


def routes_view(request):
    services = Service.objects.prefetch_related("routes__points").all()

    return render(request, "routes.html", {"services": services})
