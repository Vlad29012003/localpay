from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='permissions.log',
    level=logging.INFO,
    format= '%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# responsible role for base user
class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated and request.user.role == 'user'
        logger.info(f'User {request.user.username} accessed {view.__class__.__name__} with permission {is_authenticated}')

        return is_authenticated
    

# responsible role for supervisor
class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated and request.user.role == 'supervisor'
        logger.info(f'Supervisor {request.user.username} accessed {view.__class__.__name__} with permission {is_authenticated}')
        return is_authenticated
    

# responsible role for admin
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated and request.user.role == 'supervisor'
        logger.info(f'Admin {request.user.username} accessed {view.__class__.__name__} with permission {is_authenticated}')
        return is_authenticated