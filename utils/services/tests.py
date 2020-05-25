import datetime
import json
from django.test import TestCase

from utils.services import WeatherService


class WeatherServiceTestCase(TestCase):
    """ Test Weather Service class."""

    def test_get_weather(self):
        city = "Bucharest"
        country = "Romania"
        date = datetime.date.today()
        service = WeatherService(city, country, date)

        response = service.get_weather()
        self.assertTrue(response is not None)

        expected_fields = ["temp_c", "feels_like_c", "precip_mm", "humidity",
                           "weather_desc", "cloud_cover", "date", "location"]
        for field in expected_fields:
            self.assertTrue(field in response)

        self.assertEqual(response['date'], date.strftime("%Y-%m-%d"))

        fmt_location = "{}, {}".format(city.lower(), country.lower())
        self.assertEqual(response['location'].lower(), fmt_location)
