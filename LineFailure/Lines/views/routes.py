from django.shortcuts import render
from Lines.models.Service import Service, RoutePoint
from django.db.models import Prefetch


def routes_view(request):
    services = Service.objects.prefetch_related(
        Prefetch(
            "routes__routepoint_set",
            queryset=RoutePoint.objects.select_related("point"),
        )
    )
    return render(request, "routes.html", {"services": services})
