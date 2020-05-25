from django.db.models import Q

from jogs.models import Jog


class JogReporter:
    """Computes avg speed and avg distance for each jog that belongs to user,
    between start_week and end_week.
    """
    def __init__(self, user, start_week, end_week):
        self.user = user
        self.start_week = start_week
        self.end_week = end_week

    def _get_jogs(self):
        filters = Q(user=self.user) &\
                  Q(date__gte=self.start_week) &\
                  Q(date__lte=self.end_week)
        return Jog.objects.filter(filters)

    def _compute_report_fields(self, jogs):
        """Computes avg speed and avg distance for given jog queryset. """
        avg_speed = 0
        avg_distance = 0
        count = 0
        for jog in jogs:
            avg_distance += jog.distance
            speed = 0
            if jog.time != 0:
                speed = float(jog.distance) / jog.time
            avg_speed += speed
            count += 1

        if count > 0:
            avg_distance /= count
            avg_speed /= count

        report = {
            'avg_speed': avg_speed,
            'avg_distance': avg_distance,
            'start_date': self.start_week,
            'end_date': self.end_week
        }
        return report

    def generate_report(self):
        jogs = self._get_jogs()
        return self._compute_report_fields(jogs)
