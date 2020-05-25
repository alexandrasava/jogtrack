from utils.constants import Role


def is_admin(user):
    if user.role == Role.ADMIN:
        return True
    return False


def is_manager(user):
    if user.role == Role.MANAGER:
        return True
    return False


def is_regular(user):
    if user.role == Role.REGULAR:
        return True
    return False
