from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from datetime import timedelta
from django.utils import timezone
from django.conf import settings


def expires_in(token):
    """Return left time of the token."""
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) -\
        time_elapsed
    return left_time


def is_token_expired(token):
    """Checks if token is expired."""
    return expires_in(token) < timedelta(seconds=0)


def token_expire_handler(token):
    """Regenerates the token in case it's expired."""
    is_expired = is_token_expired(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user=token.user)
    return is_expired, token


class ExpiringTokenAuthentication(TokenAuthentication):
    """For each request, checks if token is valid or not.
    If token is expired then generate a new one.
    NOTE: this class is default for settings.py:DEFAULT_AUTHENTICATION_CLASSES
    """
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active")

        if is_token_expired(token):
            raise AuthenticationFailed("The Token is expired")

        return (token.user, token)
