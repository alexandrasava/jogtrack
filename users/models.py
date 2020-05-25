from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers.user_manager import UserManager
from utils.constants import Role


class User(AbstractUser):
    role = models.PositiveSmallIntegerField(choices=Role.ROLE_CHOIES)
    objects = UserManager()
