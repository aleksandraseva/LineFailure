from django.db import models


class Service(models.Model):
    name = models.CharField(unique=False)


class Point(models.Model):
    location = models.CharField()
    line_name = models.CharField()


class Route(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="routes"
    )
    points = models.ManyToManyField(Point)
