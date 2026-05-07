from django.db import models


class Service(models.Model):
    name = models.CharField()
    location = models.CharField()


class Point(models.Model):
    location = models.CharField()
    line_name = models.CharField()
    port = models.CharField()
    unit = models.CharField()
    chan = models.CharField()

    class Meta:
        unique_together = (
            "location",
            "line_name",
            "port",
            "unit",
            "chan",
        )


class Route(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="routes"
    )
    points = models.ManyToManyField(Point, through="RoutePoint")
    role = models.CharField()


class RoutePoint(models.Model):
    route = models.ForeignKey("Route", on_delete=models.CASCADE)
    point = models.ForeignKey("Point", on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("route", "order")
        ordering = ["order"]
