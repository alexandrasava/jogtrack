from rest_framework import serializers

from jogs.models.jog_report import JogReport
from utils.commons import mps_to_kmph, m_to_km


class JogReportSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(format="%Y-%m-%d", write_only=True)
    end_date = serializers.DateField(format="%Y-%m-%d", write_only=True)
    # m/s
    avg_speed = serializers.FloatField(write_only=True)
    # m
    avg_distance = serializers.FloatField(write_only=True)
    report = serializers.SerializerMethodField()

    class Meta:
        model = JogReport
        fields = ("avg_speed", "avg_distance", "start_date", "end_date",
                  "report")

    def get_report(self, obj):
        date_fmt = "%Y-%m-%d"
        msg =\
            "{}, your weekly jogging report for {} - {} period is:\n Average Speed: {} km/h\nAverage Distance: {} km".format(
                obj.user.username,
                obj.start_date.strftime(date_fmt),
                obj.end_date.strftime(date_fmt),
                mps_to_kmph(obj.avg_speed),
                m_to_km(obj.avg_distance))
        return msg
