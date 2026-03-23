from django.shortcuts import render
from Lines.models.Service import Service, Point, Route
from django.db.models import F, Value
from django.db.models.functions import Replace, Lower
from collections import defaultdict

line_name = ["LL 2", "LL 10"]


def connections_view(request):

    global line_name
    selected_lines = []
    services_data = []

    if request.method == "POST":
        selected_lines = request.POST.getlist("lines")
        clean_words = [word.replace(" ", "").lower() for word in selected_lines]

        services = Service.objects.none()
        for word in clean_words:

            services |= (
                Service.objects.annotate(
                    clean_line=Lower(
                        Replace(F("routes__points__line_name"), Value(" "), Value(""))
                    )
                )
                .filter(clean_line__icontains=word)
                .distinct()
            )

        for service in services:
            total_routes = service.routes.all()

            matching_routes = Route.objects.none()
            for word in clean_words:
                matching_routes |= (
                    total_routes.annotate(
                        clean_line=Lower(
                            Replace(F("points__line_name"), Value(" "), Value(""))
                        )
                    )
                    .filter(clean_line__icontains=word)
                    .distinct()
                )

            remaining_routes_count = total_routes.count() - matching_routes.count()

            services_data.append(
                {"service": service, "remaining_routes_count": remaining_routes_count}
            )
    else:
        services_data = []

    grouped_services = defaultdict(list)

    for item in services_data:
        location = item["service"].location
        grouped_services[location].append(item)

    return render(
        request,
        "lines.html",
        {
            "line_name": line_name,
            "grouped_services": dict(grouped_services),
            "selected_lines": selected_lines,
        },
    )
