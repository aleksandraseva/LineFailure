from django.db import models


class Line(models.Model):
    name = models.CharField(max_length=100)
