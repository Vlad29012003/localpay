import pytest
from rest_framework import status
from localpay.models import User_mon

@pytest.mark.django_db
def test_admin_can_create_user(authenticated_client):
    user_data = {
        "login": "newuser",
        "password": "securepassword123",
        "name": "John",
        "surname": "Doe",
        "is_staff": False,
        "is_active": True,
        "region": "Чуйская",
        "role": "user",
    }

    response = authenticated_client.post("/user/create/", user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["login"] == user_data["login"]


    created_user = User_mon.objects.get(login=user_data["login"])
    assert created_user.name == user_data["name"]
    assert created_user.surname == user_data["surname"]
    assert created_user.role == user_data["role"]


@pytest.mark.django_db
def test_create_user_fails_without_required_fields(authenticated_client):
    incomplete_user_data = {
        "login": "incompleteuser",
    }

    response = authenticated_client.post("/user/create/", incomplete_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    required_fields = ['password' , 'region']
    for fields in required_fields:
        assert fields in response.data , f"Field '{fields}' should be required" 


@pytest.mark.django_db
def test_non_admin_cannot_create_user(api_client):
    user_data = {
        "login": "unauthorizeduser",
        "password": "securepassword123",
        "name": "Jane",
        "surname": "Smith",
        "is_staff": False,
        "is_active": True,
        "region": "Чуйская",
        "role": "user",
    }

    response = api_client.post("/user/create/", user_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
