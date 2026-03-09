from django.db import models


class Connection(models.Model):
    first_location = models.CharField()
    first_unit = models.CharField()
    first_port = models.CharField()
    second_location = models.CharField()
    second_unit = models.CharField()
    second_port = models.CharField()
