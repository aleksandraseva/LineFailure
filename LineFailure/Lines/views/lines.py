from django.shortcuts import render
from Lines.models.Service import Route, RoutePoint

from django.db.models import F, Value
from django.db.models.functions import Replace, Lower

from collections import defaultdict

line_name = [
    "LL 1",
    "LL 2",
    "LL 3",
    "LL 4",
    "LL 8",
    "LL 9",
    "LL 10",
    "LL 11",
    "LL 12",
    "LL 13",
    "LL 14",
    "LL 15",
    "LL 16",
    "LL 17",
    "LL 18",
    "LL 19",
    "LL 20",
    "LL 21",
    "LL 22",
    "LL 40",
    "LL 46",
    "LL 47",
    "LL 74",
    "RR 1",
    "RR 2",
    "RR 3",
    "RR 4",
    "RR 5",
    "RR 8",
    "RR 10",
    "RR 11",
    "RR 12",
    "RR 13",
    "RR 18",
    "RR 19",
    "RR 21",
    "RR 40",
    "RR 74",
]


def connections_view(request):

    selected_lines = []
    grouped_services = defaultdict(list)

    if request.method == "POST":

        selected_lines = request.POST.getlist("lines")
        clean_words = [w.replace(" ", "").lower() for w in selected_lines]

        matched_routes = []

        for word in clean_words:

            routes = (
                Route.objects.filter(parent_route__isnull=True)
                .annotate(
                    clean_line=Lower(
                        Replace(
                            F("routepoint__point__line_name"), Value(" "), Value("")
                        )
                    )
                )
                .filter(clean_line__icontains=word)
                .select_related("service")
                .distinct()
            )

            for route in routes:
                matched_rp = (
                    RoutePoint.objects.filter(route=route)
                    .annotate(
                        clean_line=Lower(
                            Replace(F("point__line_name"), Value(" "), Value(""))
                        )
                    )
                    .filter(clean_line__icontains=word)
                    .order_by("order")
                    .first()
                )

                if not matched_rp:
                    continue

                next_points = (
                    RoutePoint.objects.filter(route=route, order__gt=matched_rp.order)
                    .select_related("point")
                    .order_by("order")
                )

                next_points_data = [
                    {
                        "line_name": rp.point.line_name,
                        "location": rp.point.location,
                        "port": rp.point.port,
                        "unit": rp.point.unit,
                        "chan": rp.point.chan,
                        "order": rp.order,
                    }
                    for rp in next_points
                ]

                matched_routes.append(
                    {
                        "route": route,
                        "type": "FAILED",
                        "color": "#ffcccc",
                        "next_points": next_points_data,
                    }
                )
                operative_routes = (
                    Route.objects.filter(
                        service=route.service, parent_route__isnull=True
                    )
                    .exclude(id=route.id)
                    .distinct()
                )

                for op_route in operative_routes:

                    operative_points = (
                        RoutePoint.objects.filter(route=op_route)
                        .select_related("point")
                        .order_by("order")
                    )

                    operative_points_data = [
                        {
                            "line_name": rp.point.line_name,
                            "location": rp.point.location,
                            "port": rp.point.port,
                            "unit": rp.point.unit,
                            "chan": rp.point.chan,
                            "order": rp.order,
                        }
                        for rp in operative_points
                    ]

                    matched_routes.append(
                        {
                            "route": op_route,
                            "type": "OPERATIVE",
                            "color": "#d4edda",
                            "next_points": operative_points_data,
                        }
                    )

        for item in matched_routes:

            route = item["route"]

            grouped_services[route.service.location].append(
                {
                    "service": route.service,
                    "route_id": route.id,
                    "type": item["type"],
                    "color": item["color"],
                    "next_points": item["next_points"],
                }
            )

    return render(
        request,
        "lines.html",
        {
            "line_name": line_name,
            "grouped_services": dict(grouped_services),
            "selected_lines": selected_lines,
        },
    )
