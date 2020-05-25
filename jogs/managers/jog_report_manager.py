import logging

from jogs.models.jog_report import JogReport
from jogs.serializers.jog_report import JogReportSerializer
from jogs.utils.reporters import JogReporter
from utils.commons import date_to_str

logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class JogReportManager:
    """Handles jog report create and udate."""

    @staticmethod
    def _create_report(user, start_week, end_week, old_report=None):
        """Generates a report. If old_report is provided, it replaces the
        old one with the newly generated one.
        """
        reporter = JogReporter(user, start_week, end_week)
        report = reporter.generate_report()

        action = ""
        if old_report:
            action = "Re"

        jr_serializer = JogReportSerializer(instance=old_report,
                                            data=report)
        if jr_serializer.is_valid():
            jr_serializer.save(user=user)
            logger.debug(
                "{}Generated report for user {} for period {} - {}"
                .format(action, user.username, date_to_str(start_week),
                        date_to_str(end_week)))
        else:
            logger.error(
                "{}Generate report error for user {}: {}"
                .format(action, user.username, jr_serializer.errors))

    @classmethod
    def create_report(cls, user, start_week, end_week):
        old_report = JogReport.objects.filter(
            user=user,
            start_date=start_week,
            end_date=end_week)

        if old_report:
            cls._create_report(user, start_week, end_week, old_report[0])
        else:
            cls._create_report(user, start_week, end_week)

    @classmethod
    def update_report(cls, user, start_week, end_week):
        old_report = JogReport.objects.filter(
            user=user,
            start_date=start_week,
            end_date=end_week)

        if not old_report:
            logger.debug(
                "There is no report to update for user {} between {} and {}"
                .format(user.username, date_to_str(start_week),
                        date_to_str(end_week)))
            return
        else:
            old_report = old_report[0]

        cls._create_report(user, start_week, end_week, old_report)
