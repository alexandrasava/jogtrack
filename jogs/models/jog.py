from django.conf import settings
from django.db import models


class Jog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    # meters
    distance = models.PositiveIntegerField()
    # seconds
    time = models.PositiveIntegerField()
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jog"
        verbose_name_plural = "Jogs"
