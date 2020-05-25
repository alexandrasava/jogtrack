from django.contrib.auth.models import BaseUserManager

from utils.constants import Role


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, **kwargs):
        email = kwargs.pop('email', False)
        email = self.normalize_email(email)
        is_staff = kwargs.pop('is_staff', False)
        is_superuser = kwargs.pop('is_superuser', False)
        role = kwargs.pop('role', Role.REGULAR)
        password = kwargs.pop('password')
        user = self.model(
            email=email,
            role=role,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, **extra_fields):
        return self._create_user(**extra_fields)

    def create_superuser(self, **extra_fields):
        return self._create_user(role=Role.ADMIN, is_staff=True,
                                 is_superuser=True, **extra_fields)

    def create_regular(self, **kwargs):
        return self._create_user(role=Role.REGULAR, **kwargs)

    def create_manager(self, **kwargs):
        return self._create_user(role=Role.MANAGER, **kwargs)

    def create_admin(self, **kwargs):
        return self._create_user(role=Role.ADMIN, **kwargs)
