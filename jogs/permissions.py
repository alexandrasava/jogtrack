from rest_framework.permissions import BasePermission

from utils.constants import Role


class UserIsOwnerOrAdmin(BasePermission):
    """ Checks if user is admin or owner of the jog entry."""

    def has_object_permission(self, request, view, jog):
        user_is_admin = request.user.role == Role.ADMIN
        is_owner = jog.user.id == request.user.id
        return user_is_admin or is_owner
