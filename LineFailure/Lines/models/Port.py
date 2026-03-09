from django.db import models


class Port(models.Model):
    port = models.CharField()
    location = models.CharField()
    role = models.CharField()
