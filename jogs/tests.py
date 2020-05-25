import datetime
import json

from django.urls import reverse

from rest_framework.test import APITestCase

from jogs.models import Jog
from users.models import User
from utils.constants import Role
from utils.tests.commons import JogTrackTestCaseMixin


class JogListCreateViewTestCase(JogTrackTestCaseMixin, APITestCase):
    """ Test jog list/create action."""
    url = reverse("jogs:list_create")

    def setUp(self):
        super().setUp()

        self.jog_data_list = [
            {
                "date": datetime.date.today(),
                "distance": 1000,
                "time": 1200,
                "country": "Romania",
                "city": "Bucharest"
            },
            {
                "date": datetime.date.today() - datetime.timedelta(days=8),
                "distance": 5000,
                "time": 2400,
                "country": "United Kingdom",
                "city": "London"
            },
            {
                "date": datetime.date.today() - datetime.timedelta(days=14),
                "distance": 10000,
                "time": 3600,
                "country": "France",
                "city": "Paris"
            },
            {
                "date": datetime.date.today() - datetime.timedelta(days=4),
                "distance": 20000,
                "time": 6600,
                "country": "France",
                "city": "Paris"
            },
            {
                "date": datetime.date.today() - datetime.timedelta(days=2),
                "distance": 4000,
                "time": 1800,
                "country": "Romania",
                "city": "Bucharest"
            }
        ]
        for role in [Role.ADMIN, Role.MANAGER, Role.REGULAR]:
            user = self.users[role]
            for jog_data in self.jog_data_list:
                Jog.objects.create(user=user, **jog_data)

    def test_list_unauthenticated(self):
        """Test to verify list users without authentication"""
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_list(self):
        """Test to verify list jogs action by all roles."""

        for role in [Role.REGULAR, Role.ADMIN, Role.MANAGER]:
            self._login(role)
            response = self.client.get(self.url)
            self.assertEqual(200, response.status_code)

            list_len = json.loads(response.content.decode('utf-8'))['count']
            if role == Role.ADMIN:
                # An admin sees all jogs from the DB.
                correct_len = Jog.objects.filter().count()
            else:
                # A regular user sees only his jogs.
                correct_len = Jog.objects.filter(user=self.users[role]).count()

            self.assertTrue(list_len == correct_len)

    def test_list_filters(self):
        """Test to verify list jogs action with filters."""
        past_date = datetime.date.today() - datetime.timedelta(days=7)

        filters = "(date gte {}) AND ((distance lte 3000) OR (city eq Paris))".format(past_date.strftime("%Y-%m-%d"))

        url = "{}?search={}".format(self.url, filters)

        self._login(Role.REGULAR)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        jogs = Jog.objects.filter(user=self.users[Role.REGULAR])
        correct_len = 0
        for jog in jogs:
            if jog.date >= past_date:
                if jog.distance <= 3000 or jog.city == 'Paris':
                    correct_len += 1

        list_len = json.loads(response.content.decode('utf-8'))['count']
        self.assertTrue(list_len == correct_len)

    def test_create(self):
        """Test create jog."""
        jog_data = {
            "date": datetime.date.today(),
            "distance": 4000,
            "time": 1800,
            "location": "Bucharest, Romania",
        }

        self._login(Role.REGULAR)

        response = self.client.post(self.url, jog_data)
        self.assertEqual(201, response.status_code)

        correct_len = len(self.jog_data_list) + 1
        nr_jogs = Jog.objects.filter(user=self.users[Role.REGULAR]).count()
        self.assertTrue(nr_jogs == correct_len)

    def test_create_for_user(self):
        """Test create jog by a user for a another user."""
        jog_data = {
            "date": datetime.date.today(),
            "distance": 4000,
            "time": 1800,
            "location": "Bucharest, Romania",
            "owner": self.users[Role.MANAGER].id
        }

        # Admin tries to create a jog for another user
        self._login(Role.ADMIN)

        response = self.client.post(self.url, jog_data)
        self.assertEqual(201, response.status_code)

        # Admin should be able to create a jog for other user.
        correct_len = len(self.jog_data_list) + 1
        nr_jogs = Jog.objects.filter(user=self.users[Role.MANAGER]).count()
        self.assertTrue(nr_jogs == correct_len)

        # Regular tries to create a jog for another user.
        self._login(Role.REGULAR)

        # If a regular user tries to create a jog for other user (owner set),
        # the jog will be created on it's account (owner value will
        # be ignored.)
        response = self.client.post(self.url, jog_data)
        self.assertEqual(201, response.status_code)

        for role in [Role.REGULAR, Role.MANAGER]:
            nr_jogs = Jog.objects.filter(user=self.users[role]).count()
            self.assertTrue(nr_jogs == correct_len)


class UserRetrieveUpdateDestroyCase(JogTrackTestCaseMixin, APITestCase):
    """Test retrrieve, update, delete actions."""

    def url(self, jog):
        return reverse("jogs:jog_rud", kwargs={"pk": jog.pk})

    def setUp(self):
        super().setUp()
        jog_data = {
            "date": datetime.date.today(),
            "distance": 1000,
            "time": 1200,
            "country": "Romania",
            "city": "Bucharest"
        }
        self.jogs = {}
        for role in [Role.ADMIN, Role.MANAGER, Role.REGULAR]:
            user = self.users[role]
            jog = Jog.objects.create(user=user, **jog_data)
            self.jogs[role] = jog

    def test_get(self):
        """Test to verify get jog request."""
        self._login(Role.REGULAR)

        # Retrieve own jog as regular user.
        jog_url = self.url(self.jogs[Role.REGULAR])
        response = self.client.get(jog_url)
        self.assertEqual(200, response.status_code)

        # Regular and manager users are not allowed to retrieve other users jogs).
        for role in [Role.REGULAR, Role.MANAGER]:
            jog_url = self.url(self.jogs[Role.ADMIN])
            self._login(role)
            response = self.client.get(jog_url)
            self.assertEqual(403, response.status_code)

        # Admin can retrieve jogs from any user.
        self._login(Role.ADMIN)
        jog_url = self.url(self.jogs[Role.MANAGER])
        response = self.client.get(jog_url)
        self.assertEqual(200, response.status_code)

    def _assertEqualUpdate(self, update_content, jog):
        for key in update_content:
            if key == 'date':
                new_val = jog.date.strftime("%Y-%m-%d")
            elif key == 'location':
                new_val = "{},{}".format(jog.city, jog.country)
            else:
                new_val = getattr(jog, key, None)
            self.assertEqual(update_content[key], new_val)

    def test_update(self):
        """Test to verify update jogs (PUT & PATCH) actions."""
        self._login(Role.REGULAR)

        manager_jog_url = self.url(self.jogs[Role.MANAGER])
        regular_jog_url = self.url(self.jogs[Role.REGULAR])

        patch_content = {
            "time": 999,
        }
        # Test PATCH on users's jog.
        response = self.client.patch(regular_jog_url, patch_content)
        self.assertEqual(200, response.status_code)
        new_jog = Jog.objects.get(id=self.jogs[Role.REGULAR].id)
        self.assertEqual(new_jog.time, patch_content['time'])

        # Test PATCH on manager's jog as regular user.
        response = self.client.patch(manager_jog_url, patch_content)
        self.assertEqual(403, response.status_code)

        # Test PATCH Admin on other user's jog.
        self._login(Role.ADMIN)
        patch_content = {
            "distance": 777,
        }
        response = self.client.patch(regular_jog_url, patch_content)
        self.assertEqual(200, response.status_code)
        new_jog = Jog.objects.get(id=self.jogs[Role.REGULAR].id)
        self.assertEqual(new_jog.distance, patch_content['distance'])

        put_content = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "distance": 111,
            "time": 222,
            "location": "Buenos Aires,Argentina",
        }

        # Test PUT on users's jog.
        self._login(Role.REGULAR)
        response = self.client.put(regular_jog_url, put_content)
        self.assertEqual(200, response.status_code)
        new_jog = Jog.objects.get(id=self.jogs[Role.REGULAR].id)
        self._assertEqualUpdate(put_content, new_jog)

        # Test PUT on manager's jog as regular user.
        response = self.client.put(manager_jog_url, put_content)
        self.assertEqual(403, response.status_code)

        # Test PUT Admin on other user's jog.
        self._login(Role.ADMIN)
        put_content = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "distance": 444,
            "time": 555,
            "location": "New York,United States of America",
        }
        response = self.client.put(regular_jog_url, put_content)
        self.assertEqual(200, response.status_code)
        new_jog = Jog.objects.get(id=self.jogs[Role.REGULAR].id)
        self._assertEqualUpdate(put_content, new_jog)

    def test_delete(self):
        """Test to verify delete jogs action."""
        self._login(Role.REGULAR)

        # Delete jog as regular user.
        regular_jog_url = self.url(self.jogs[Role.REGULAR])
        response = self.client.delete(regular_jog_url)
        self.assertEqual(204, response.status_code)
        nr_jogs = Jog.objects.filter(user=self.users[Role.REGULAR]).count()
        self.assertEqual(nr_jogs, 0)

        # Delete other user's jogs having regular / manager role.
        admin_jog_url = self.url(self.jogs[Role.ADMIN])
        for role in [Role.REGULAR, Role.MANAGER]:
            self._login(role)
            response = self.client.delete(admin_jog_url)
            self.assertEqual(403, response.status_code)

        # Delete other user's jogs having admin role.
        self._login(Role.ADMIN)
        manager_jog_url = self.url(self.jogs[Role.MANAGER])
        response = self.client.delete(manager_jog_url)
        self.assertEqual(204, response.status_code)
        nr_jogs = Jog.objects.filter(user=self.users[Role.MANAGER]).count()
        self.assertEqual(nr_jogs, 0)
