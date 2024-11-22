import pytest
from rest_framework.test import APIClient
from localpay.models import User_mon
from django.contrib.auth import get_user_model
import factory

User = get_user_model()




class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User_mon
        skip_postgeneration_save = True
    
    login = factory.Sequence(lambda n: f'user{n}')
    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_staff = False
    is_active = True
    region = 'Чуйская'
    role = 'user'


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return UserFactory(
        is_staff=True, 
        login='admin', 
        role='admin',
        is_active=True
    )

@pytest.fixture
def authenticated_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client