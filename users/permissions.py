from utils.constants import Role

from rest_framework.permissions import BasePermission


class UserCanRUD(BasePermission):
    """ Checks if user can read, update, delete an entry.
    Users that have admin or manager roles can RUD any database entry. Note:
    managers can't rud admins.
    Regular users are allowed to RUD only their database entry.
    """
    def has_object_permission(self, request, view, user):
        user_is_authority = (request.user.role in [Role.ADMIN, Role.MANAGER])
        user_is_authority = user_is_authority and user.role <= request.user.role
        user_is_owner = (request.user.id == user.id)
        return user_is_owner or user_is_authority


class UserIsAuthority(BasePermission):
    """ Checks if user is admin or manager."""
    @staticmethod
    def is_authority(user):
        return user.role in [Role.ADMIN, Role.MANAGER]

    def has_object_permission(self, request, view, user):
        return self.is_authority(request.user)

    def has_permission(self, request, view):
        return self.is_authority(request.user)
