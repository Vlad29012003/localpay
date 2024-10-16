from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='permissions.log',
    level=logging.INFO,
    format= '%(asctime)s - %(levelname)'
)

# responsible role for base user
class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'
        logger.info(f'User {request.user.username}')
    

# responsible role for supervisor
class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supervisor'
        logger.info(f'User {request.user.username}')
    

# responsible role for admin
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'