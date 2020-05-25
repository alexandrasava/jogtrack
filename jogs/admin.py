from django.contrib import admin
from jogs.models import Jog, JogReport, WeatherConditions

admin.site.register(Jog)
admin.site.register(JogReport)
admin.site.register(WeatherConditions)
