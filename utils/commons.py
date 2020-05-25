import datetime
import logging
import requests

from utils.constants import Role

logger = logging.getLogger('jogtrack')
logger.setLevel(logging.INFO)


def get_request(url, params):
    """ Makes a GET request.

    Parameters
    ----------
    url (str): URL path for the request.
    params (dict): HTTP GET parameters.
    """
    try:
        r = requests.get(url=url, params=params)
    except requests.exceptions.RequestException as e:
        logger.error(
            'Exception while executing GET request: {}'
            .format(e)
        )
        return None

    if r.status_code != 200:
        logger.warning(
            "GET response returned {} code."
            .format(r.status_code))
        return None

    try:
        return r.json()
    except ValueError as e:
        logger.error(
            'GET response can\'t be JSON decoded: {}'
            .format(e)
        )
        return None


def kmph_to_mps(kmph):
    """Convert speed from km/h in m/sec."""
    return (0.277778 * kmph)


def mps_to_kmph(mps):
    """Convert speed from m/sec in km/h."""
    return (3.6 * mps)


def m_to_km(m):
    """Convert length unit from m to km."""
    return float(m) / 1000


def get_role_name(role_id):
    role_names = {
        Role.REGULAR: "REGULAR",
        Role.MANAGER: "MANAGER",
        Role.ADMIN: "ADMIN"
    }

    return role_names.get(role_id, None)


def get_week(date):
    """Returns start and end dates of the week."""
    weekday = date.weekday()
    start_week = date - datetime.timedelta(days=weekday)
    end_week = start_week + datetime.timedelta(days=6)
    return start_week, end_week


def date_to_str(date):
    """Returns a date in a string format."""
    return date.strftime("%Y-%m-%d")
