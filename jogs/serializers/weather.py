from rest_framework import serializers
from jogs.models.weather import WeatherConditions


class WeatherConditionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherConditions
        fields = ("id", "temp_c", "feels_like_c", "precip_mm", "humidity",
                  "cloud_cover", "weather_desc")
