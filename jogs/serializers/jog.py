import logging

from rest_framework import serializers
from jogs.models.jog import Jog
from jogs.serializers.weather import WeatherConditionsSerializer
from users.models import User
from utils.commons import get_role_name
from utils.permissions import is_admin

logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class LocationSerializer(serializers.Field):

    def to_representation(self, obj):
        return "{},{}".format(obj.city, obj.country)

    def to_internal_value(self, data):
        tokens = data.split(",")
        if len(tokens) < 2:
            msg = 'Location must have the following format: $city,$country'
            raise serializers.ValidationError(msg)

        return {
            'city': tokens[0].strip(),
            'country': tokens[1].strip()
        }


class JogSerializer(serializers.ModelSerializer):
    location = LocationSerializer(source='*')
    weather = WeatherConditionsSerializer(source='weatherconditions',
                                          read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    owner = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Jog
        fields = ("id", "date", "distance", "time", "weather", "location",
                  "owner")

    def validate_owner(self, user_id):
        request = self.context.get('request', None)

        if request and request.method == 'POST':
            if is_admin(request.user) and user_id:
                users = User.objects.filter(id=user_id)
                if not users:
                    raise serializers.ValidationError('User does not exist')
                return users[0]
        return None

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        # If owner user exists, it means an admin/manager wants to create
        # an entry for that user.
        if owner:
            # Change the user value (which is the user who made the request)
            # with owner value.
            logger.debug(
                "{} creates jog for user {}"
                .format(get_role_name(validated_data['user'].role),
                        owner.username))
            validated_data['user'] = owner
        else:
            logger.debug(
                "Create jog (user {})"
                .format(validated_data['user'].username))

        jog = Jog.objects.create(**validated_data)

        return jog
