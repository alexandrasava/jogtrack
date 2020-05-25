from django.db import models

from jogs.models.jog import Jog


class WeatherConditions(models.Model):
    jog = models.OneToOneField(Jog, on_delete=models.CASCADE)
    temp_c = models.IntegerField()
    feels_like_c = models.IntegerField()
    precip_mm = models.FloatField()
    humidity = models.IntegerField()
    cloud_cover = models.PositiveIntegerField()
    weather_desc = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Weather Conditions"
        verbose_name_plural = "Weather Conditions"