import datetime
import logging

from django.conf import settings

from utils.commons import get_request


logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class WeatherService:
    """Calls WorldWeatherOnline API and grabs the weather."""
    API_ENDPOINT = "http://api.worldweatheronline.com/premium/v1/past-weather.ashx"

    def __init__(self, city, country, date):
        self.city = city
        self.country = country
        self.date = date

    def _call_api(self):
        """Calls the Weather API with the appropriate parameters."""
        params = {
            "q": "{},{}".format(
                self.city.replace(" ", "+"),
                self.country.replace(" ", "+")),
            "date": self.date.strftime("%Y-%m-%d"),
            "tp": 24,  # Time interval in hours.
            "format": "json",
            "key": settings.WEATHER_API_KEY
        }
        return get_request(self.API_ENDPOINT, params)

    @staticmethod
    def _capitalize(string):
        """ Capitalizes each token from a string.
        eg. new york -> New York
        """
        tokens = string.split(" ")
        tokens = [token.capitalize() for token in tokens]
        return ' '.join(tokens)

    def _validate_api_response(self, response):
        """Make sure the response is for the requested city & country.
        This is because in case the city does not exist, the api will
        return data for cities with similar names from other countries.
        """
        if "data" not in response:
            return False

        if "error" in response["data"]:
            logger.warning("Weather API returned: %s" % (
                response["data"]["error"]))
            return False

        location = "{}, {}".format(self.city.lower(),
                                   self.country.lower())
        response_location = response["data"]["request"][0]["query"].lower()
        if location != response["data"]["request"][0]["query"].lower():
            logger.warning(
                "Requested location doesn't match: {} vs {}"
                .format(location, response_location))
            return False

        return True

    @staticmethod
    def _parse_api_response(response):
        """Extracts the needed fields from the api response."""
        try:
            weather = response["data"]["weather"][0]["hourly"][0]
            return {
                "location": response["data"]["request"][0]["query"],
                "date": response["data"]["weather"][0]["date"],
                "temp_c": weather["tempC"],
                "feels_like_c": weather["FeelsLikeC"],
                "precip_mm": weather["precipMM"],
                "cloud_cover": weather["cloudcover"],
                "humidity": weather["humidity"],
                "weather_desc": weather["weatherDesc"][0]['value']
            }
        except KeyError as e:
            logger.error(e)
            return None

    def get_weather(self):
        # We don't support forecasting.
        if self.date > datetime.date.today():
            return None
        resp = self._call_api()
        if not resp:
            return None

        if not self._validate_api_response(resp):
            return None

        return self._parse_api_response(resp)
