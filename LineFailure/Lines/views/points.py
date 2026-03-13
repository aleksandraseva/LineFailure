from django.shortcuts import render
from Lines.models.Service import Service, Point, Route
from Lines.services.MUXParser import *
from Lines.forms.FormItem import FormItem


# def service_points(request):
# find_all_service()
# service = Service.objects.prefetch_related("routes__points").get(
#     name="port-2: SAR/J_123.100"
# )

# service = Service.objects.filter(
#     routes__points__line_name__icontains="LL 2"
# ).distinct()

# return render(request, "points.html", {"services": service})


def select_items_view(request):
    if request.method == "POST":
        form = FormItem(request.POST)
        if form.is_valid():
            selected_items = form.cleaned_data["items"]
            print(selected_items)  # samo za debug
            return render(
                request, "app/thank_you.html", {"selected_items": selected_items}
            )
    else:
        form = FormItem()
    return render(request, "points.html", {"form": form})
