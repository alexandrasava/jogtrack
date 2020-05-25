import datetime

from django.core.management.base import BaseCommand, CommandError
import logging

from jogs.managers.jog_report_manager import JogReportManager
from jogs.utils.reporters import JogReporter
from jogs.serializers.jog_report import JogReportSerializer
from users.models import User
from utils.commons import get_week

logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    help = 'Generate report on average speed & distance per week for each user'

    @staticmethod
    def _get_prev_week():
        """Returns start(Monday) and end(Sunday) dates for the previous week."""
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        start_last_week, end_last_week = get_week(last_week)
        return start_last_week, end_last_week

    def handle(self, *args, **options):
        start_week, end_week = self._get_prev_week()
        user_qs = User.objects.all()

        for user in user_qs:
            JogReportManager.create_report(user, start_week, end_week)
