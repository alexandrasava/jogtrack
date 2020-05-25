import logging

from jogs.managers.jog_report_manager import JogReportManager
from jogs.models import Jog
from jogs.serializers.jog import JogSerializer
from jogs.serializers.weather import WeatherConditionsSerializer
from jogs.utils.reporters import JogReporter
from utils.commons import get_week
from utils.services.weather import WeatherService

logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class JogManager():
    """Handles jog create update and delete."""
    def __init__(self, jog):
        self.jog = jog

    @classmethod
    def create_jog(cls, jog_serializer, user):
        """Creates a jog."""
        jog = jog_serializer.save(user=user)
        # Create weather for jog.
        cls._create_weather(jog)

        # Trigger report regeneration.
        JogManager(jog).on_jog_cud()

        return jog

    @staticmethod
    def _create_weather(jog, old_weather=None):
        """Creates weather instance for jog, depending on location and date."""
        weather_service = WeatherService(jog.city, jog.country, jog.date)
        weather_data = weather_service.get_weather()
        if weather_data:
            weather_serializer = WeatherConditionsSerializer(
                instance=old_weather, data=weather_data)
            if weather_serializer.is_valid():
                weather_serializer.save(jog=jog)
                return True
        return False

    @staticmethod
    def _has_changed(obj1, obj2, field):
        """ Check if objects have different values for the field."""
        if obj1.get(field) != obj2.get(field):
            return True
        return False

    def update_jog(self, update_serializer, partial=False):
        """ Updates a jog."""
        old_jog = self.jog
        old_jog_s = JogSerializer(old_jog).data

        new_jog = update_serializer.save()
        logger.debug(
            "Update Jog #{} for user {}"
            .format(new_jog.id, new_jog.user.username))

        new_jog_s = JogSerializer(new_jog).data

        get_weather = False
        check_fields = ["date", "location"]
        for field in check_fields:
            has_changed = self._has_changed(old_jog_s, new_jog_s, field)
            get_weather |= has_changed

        # Only if the date or location have changed, we get the
        # weather conditions for the new values.
        if get_weather:
            old_weather = getattr(new_jog, 'weatherconditions', None)
            created = self._create_weather(new_jog, old_weather)
            if not created and old_weather:
                old_weather.delete()
                logger.debug(
                    "Delete Weather for Jog #{}"
                    .format(new_jog.id))

        return Jog.objects.get(id=new_jog.id)

    def _update_report(self):
        """Updates the report for the week of the jog."""
        start_week, end_week = get_week(self.jog.date)
        JogReportManager.update_report(self.jog.user, start_week, end_week)

    def on_jog_cud(self):
        """Actions performed when a jog is created/updated/deleted."""

        # If a jog has been created/updated/deleted, we have to update the
        # report from that week.
        logger.debug("On Jog create action.")
        self._update_report()
