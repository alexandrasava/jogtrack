import json
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User
from utils.constants import Role
from utils.tests.commons import JogTrackTestCaseMixin


class UserRegistrationViewTestCase(APITestCase):
    """ Tests the user registration flow."""
    url = reverse("users:register")

    def test_invalid_password(self):
        """Test to verify user registration with unmatching passwords."""
        user_data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "Password1!",
            "role": Role.REGULAR,
            "confirm_password": "INVALID_Password1!"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(400, response.status_code)

    def test_weak_password(self):
        """Test to verify user registration with a weak password."""
        user_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "weak_password",
            "role": Role.REGULAR,
            "confirm_password": "weak_password"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(400, response.status_code)

    def test_user_registration(self):
        """Test to verify user registration with valid data"""
        user_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "PasswordTestUser1!",
            "confirm_password": "PasswordTestUser1!"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(201, response.status_code)
        resp_content = json.loads(response.content.decode('utf-8'))
        self.assertTrue("auth_token" in resp_content)
        self.assertEqual(resp_content['role'], Role.REGULAR)

    def test_register_as_manager(self):
        """Test to verify user registration with manager and admin roles.
        Regardless of what role is specified, user will be created with
        REGULAR role.
        """
        user_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "PasswordTestUser1!",
            "confirm_password": "PasswordTestUser1!"
        }
        for idx, role in enumerate([Role.MANAGER, Role.ADMIN]):
            user_data['username'] = "{}{}".format(user_data['username'], idx)
            user_data['role'] = role
            response = self.client.post(self.url, user_data)
            self.assertEqual(201, response.status_code)
            resp_content = json.loads(response.content.decode('utf-8'))
            self.assertEqual(resp_content['role'], Role.REGULAR)

    def test_unique_username_validation(self):
        """Test to verify user registration with already exists username."""
        user_data_1 = {
            "username": "testuser",
            "email": "test@gmail.com",
            "role": Role.REGULAR,
            "password": "PasswordTestUser1!",
            "confirm_password": "PasswordTestUser1!"
        }
        response = self.client.post(self.url, user_data_1)
        self.assertEqual(201, response.status_code)

        user_data_2 = {
            "username": "testuser",
            "email": "test2@gmail.com",
            "role": Role.REGULAR,
            "password": "PasswordTestUser2!",
            "confirm_password": "PasswordTestUser2!"
        }
        response = self.client.post(self.url, user_data_2)
        self.assertEqual(400, response.status_code)

    def test_invalid_role(self):
        """Test to verify user registration with an invalid role."""
        INVALID_ROLE = 5
        user_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "role": INVALID_ROLE,
            "password": "TestUserGmail1!",
            "confirm_password": "TestUserGmail1!"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(400, response.status_code)


class UserLoginViewTestCase(APITestCase):
    """Tests the user login flow."""
    url = reverse("users:login")

    def setUp(self):
        self.username = "testuser"
        self.password = "TestUserPassword1!"
        user_data = {
            "username": self.username,
            "email": "test@gmail.com",
            "role": Role.REGULAR,
            "password": self.password,
        }
        User.objects.create_user(**user_data)

    def test_authentication_without_password(self):
        """Test to verify login without password."""
        response = self.client.post(self.url, {"username": self.username})
        self.assertEqual(400, response.status_code)

    def test_authentication_with_wrong_password(self):
        """Test to verify login with wrong password."""
        data = {
            "username": self.username,
            "password": "ITS_NOT_MY_PASSWORD"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_authentication_with_valid_data(self):
        """Test to verify login with valid credentials."""
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(200, response.status_code)
        resp_content = json.loads(response.content.decode('utf-8'))
        self.assertTrue("auth_token" in resp_content)


class UserListCreateViewTestCase(JogTrackTestCaseMixin, APITestCase):
    """ Test user list action."""
    url = reverse("users:list_create")

    def test_list_unauthenticated(self):
        """Test to verify list users without authentication"""
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_list_regular(self):
        """Test to verify list users action by a regular user."""
        self._login(Role.REGULAR)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_list(self):
        """Test to verify list users action by an admin and a manager."""

        for role in [Role.ADMIN, Role.MANAGER]:
            self._login(role)
            response = self.client.get(self.url)
            self.assertEqual(200, response.status_code)
            list_len = json.loads(response.content.decode('utf-8'))['count']
            self.assertTrue(list_len == User.objects.count())

    def test_list_filters(self):
        """Test to verify list users action with filters."""
        filters = "((username eq regular_user) OR (role gte 2)) AND (email eq manager@gmail.com)"
        url = "{}?search={}".format(self.url, filters)
        self._login(Role.MANAGER)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        list_len = json.loads(response.content.decode('utf-8'))['count']
        self.assertTrue(list_len == 1)

    def test_create_by_admin(self):
        """Test create user by admin"""

        user_data_list = [{
            "username": "testuser1",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!"
        }, {
            "username": "testuser2",
            "email": "test2@gmail.com",
            "role": Role.REGULAR,
            "password": "Test2UserGmail1!",
            "confirm_password": "Test2UserGmail1!"
        }, {
            "username": "testuser3",
            "email": "test2@gmail.com",
            "role": Role.MANAGER,
            "password": "Test2UserGmail1!",
            "confirm_password": "Test2UserGmail1!"
        }, {
            "username": "testuser4",
            "email": "test2@gmail.com",
            "role": Role.ADMIN,
            "password": "Test2UserGmail1!",
            "confirm_password": "Test2UserGmail1!"
        }]

        self._login(Role.ADMIN)
        for user_data in user_data_list:
            response = self.client.post(self.url, user_data)
            self.assertEqual(201, response.status_code)
            qs = User.objects.filter(username=user_data['username'],
                                     role=user_data.get('role', Role.REGULAR))
            self.assertTrue(qs.count() == 1)

    def test_create_by_manager(self):
        # Create users by manager.
        user_data = {
            "username": "testuser1",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!",
            "role": Role.ADMIN,
        }
        self._login(Role.MANAGER)
        response = self.client.post(self.url, user_data)
        self.assertEqual(400, response.status_code)

        user_data_list = [{
            "username": "testuser2",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!",
        }, {
            "username": "testuser3",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!",
            "role": Role.REGULAR,
        }, {
            "username": "testuser4",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!",
            "role": Role.MANAGER,
        }]

        for user_data in user_data_list:
            response = self.client.post(self.url, user_data)
            self.assertEqual(201, response.status_code)
            qs = User.objects.filter(username=user_data['username'],
                                     role=user_data.get('role', Role.REGULAR))

    def test_create_by_regular(self):
        """Test create user by a regular user."""
        user_data = {
            "username": "testuser1",
            "email": "test1@gmail.com",
            "password": "Test1UserGmail1!",
            "confirm_password": "Test1UserGmail1!"
        }
        self._login(Role.REGULAR)
        response = self.client.post(self.url, user_data)
        self.assertEqual(403, response.status_code)


class UserRetrieveUpdateDestroyCase(JogTrackTestCaseMixin, APITestCase):
    """Test retrieve, update, delete actions."""
    def url(self, user):
        return reverse("users:user_rud", kwargs={"pk": user.pk})

    def test_retrieve(self):
        """Test to verify get request."""
        self._login(Role.REGULAR)
        manager_url = self.url(self.users[Role.MANAGER])
        response = self.client.get(manager_url)
        self.assertEqual(403, response.status_code)

        regular_url = self.url(self.users[Role.REGULAR])
        response = self.client.get(regular_url)
        self.assertEqual(200, response.status_code)

        self._login(Role.MANAGER)
        response = self.client.get(regular_url)
        self.assertEqual(200, response.status_code)

        admin_url = self.url(self.users[Role.ADMIN])
        response = self.client.get(admin_url)
        # Manager is  not allowed to view admin's account.
        self.assertEqual(403, response.status_code)

    def test_update_regular_user(self):
        """Test to verify regular user is allowed to update it's data.
        """
        self._login(Role.REGULAR)
        manager_url = self.url(self.users[Role.MANAGER])
        patch_content = {
            "email": "you_were_hacked@gmail.com"
        }
        # Test PATCH on manager's account
        response = self.client.patch(manager_url, patch_content)
        self.assertEqual(403, response.status_code)

        put_content = {
            "username": "hacked_manager_user",
            "email": "hacked_manager@gmail.com",
            "role": Role.REGULAR,
            "password": "ManagerPassword1!",
            "confirm_password": "ManagerPassword1!"
        }
        # Test PUT on manager's account
        response = self.client.put(manager_url, put_content)
        self.assertEqual(403, response.status_code)

        regular_url = self.url(self.users[Role.REGULAR])
        patch_content = {
            "email": "change_my_email@gmail.com"
        }
        # Test PATCH on user's own account
        response = self.client.patch(regular_url, patch_content)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(patch_content["email"], resp_data.get("email", ""))

        put_content = {
            "username": "changed_regular_user_patch",
            "email": "changed_regular_user_patch@gmail.com",
            "role": Role.REGULAR,
            "password": "NewRegularPassword1!",
            "confirm_password": "NewRegularPassword1!"
        }
        # Test PUT on user's own account
        response = self.client.put(regular_url, put_content)
        self.assertEqual(200, response.status_code)

        resp_data = json.loads(response.content.decode('utf-8'))
        for field in ["username", "email", "role"]:
            self.assertEqual(put_content[field], resp_data.get(field, ""))

        # Test login with new pasword
        credentials = {
            "username": put_content["username"],
            "password": put_content["password"]
        }
        response = self.client.post(reverse("users:login"), credentials)
        self.assertEqual(200, response.status_code)

    def test_role_promotion(self):
        """Test to verify if users can change roles."""
        
        self._login(Role.REGULAR)
        regular_url = self.url(self.users[Role.REGULAR])
        for role in [Role.MANAGER, Role.ADMIN]:
            patch_content = {
                'role': role
            }
            response = self.client.patch(regular_url, patch_content)
            # Can't do role promotion as a regular user.
            self.assertEqual(400, response.status_code)

        self._login(Role.MANAGER)
        response = self.client.patch(regular_url, {'role': Role.MANAGER})
        # As a manager, you can promote a user up to MANAGER role.
        self.assertEqual(200, response.status_code)
        user = User.objects.get(username=self.users[Role.REGULAR].username)
        self.assertEqual(user.role, Role.MANAGER)

        response = self.client.patch(regular_url, {'role': Role.ADMIN})
        # As manager, can't promote a user to admin.
        self.assertEqual(400, response.status_code)

        user.role = Role.REGULAR
        user.save()

        self._login(Role.ADMIN)
        for role in [Role.MANAGER, Role.ADMIN]:
            response = self.client.patch(regular_url, {'role': role})
            # As ADMIN, you can promote a user to any role.
            self.assertEqual(200, response.status_code)
            user = User.objects.get(username=self.users[Role.REGULAR].username)
            self.assertEqual(user.role, role)




    def test_delete_regular_user(self):
        """Test to verify regular user is allowed to delete only it's account.
        """
        self._login(Role.REGULAR)

        manager_url = self.url(self.users[Role.MANAGER])
        response = self.client.delete(manager_url)
        # Regular user is not allowed to delete other user.
        self.assertEqual(403, response.status_code)

        before_nr_users = User.objects.all().count()

        regular_url = self.url(self.users[Role.REGULAR])
        self._login(Role.REGULAR)
        response = self.client.delete(regular_url)
        self.assertEqual(204, response.status_code)

        after_nr_users = User.objects.all().count()
        self.assertEqual(after_nr_users, before_nr_users - 1)

        self._login(Role.MANAGER)
        admin_url = self.url(self.users[Role.ADMIN])
        # Manager is not allowed to delete admin's account.
        response = self.client.delete(admin_url)
        self.assertEqual(403, response.status_code)
