from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class JogReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # In m/s
    avg_speed = models.FloatField(validators=[MinValueValidator(0)])
    # In m
    avg_distance = models.FloatField(validators=[MinValueValidator(0)])
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "JogReport"
        verbose_name_plural = "JogReports"
        unique_together = ('user', 'start_date', 'end_date',)
