from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

import django.contrib.auth.password_validation as validators

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.authentication import expires_in
from users.models import User
from utils.commons import get_role_name
from utils.constants import Role


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Role.ROLE_CHOIES, required=False)
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S",
                                            required=False, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "date_joined", "role",
                  "confirm_password")

    def validate(self, attrs):
        attr_role = attrs.get('role', 0)
        request_user = self.context['request'].user
        # If the request was made by an authenticated user (so it's not register)
        if getattr(request_user, 'role', None) is not None:
            if request_user.role < attr_role:
                # Users can't create/edit other users with higher roles.
                raise serializers.ValidationError({
                    'role': "Role can be maximum {}"
                    .format(get_role_name(request_user.role))})
        else:
            # Upon registration, set user's role REGULAR
            attrs['role'] = Role.REGULAR

        if 'password' not in attrs:
            return attrs

        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {"confirm_password": "Password doesn't match."})

        errors = {}
        try:
            # check if password passes all validiators configured in
            # AUTH_PASSWORD_VALIDATORS
            validators.validate_password(password=attrs.get('password'))
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        del attrs['confirm_password']
        attrs['password'] = make_password(attrs['password'])

        return attrs

    def create(self, validated_data):
        if 'role' not in validated_data:
            # If role is not explicitly provided, create regular users.
            return User.objects.create_regular(**validated_data)
        return User.objects.create(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    default_error_messages = {
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Invalid username or password.')
    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get("username"),
                                 password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(
                    self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials'])


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')
    expires = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Token
        fields = ("auth_token", "created", "expires")

    def get_expires(self, obj):
        val = expires_in(obj)
        return int(val.seconds)
