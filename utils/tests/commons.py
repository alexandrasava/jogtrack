from rest_framework.authtoken.models import Token

from jogs.models import Jog
from users.models import User
from utils.constants import Role


class JogTrackTestCaseMixin:
    def setUp(self):
        user_data_list = {
            Role.REGULAR: {
                "username": "regular_user",
                "email": "regular@gmail.com",
                "role": Role.REGULAR,
                "password": "RegularPassword1!",
            },
            Role.MANAGER: {
                "username": "manager_user",
                "email": "manager@gmail.com",
                "role": Role.MANAGER,
                "password": "ManagerPassword1!",
            },
            Role.ADMIN: {
                "username": "admin_user",
                "email": "admin@gmail.com",
                "role": Role.ADMIN,
                "password": "AdminPassword1!",
            }
        }

        self.users = {}
        for user_type in user_data_list:
            user_data = user_data_list[user_type]
            user = User.objects.create_user(**user_data)
            self.users[user_type] = user

    def _login(self, role):
        token, _ = Token.objects.get_or_create(user=self.users[role])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
