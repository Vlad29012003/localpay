import pytest
from rest_framework import status
from localpay.models import User_mon


# Проверка на создание юзера только для админа
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
    # отправка тестовых данных на эндпоинт
    response = authenticated_client.post("/user/create/", user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["login"] == user_data["login"]

    # Проверка данных ответа
    #Запрашивается пользователь из базы данных с помощью ORM
    created_user = User_mon.objects.get(login=user_data["login"])
    # Проверка полей сохраненного пользователя
    assert created_user.name == user_data["name"]
    assert created_user.surname == user_data["surname"]
    assert created_user.role == user_data["role"]


# Проверка обязательных полей для создания юзеров
@pytest.mark.django_db
def test_create_user_fails_without_required_fields(authenticated_client):
    incomplete_user_data = {
        "login": "incompleteuser",
    }

    # отправка тестовых данных на эндпоинт
    response = authenticated_client.post("/user/create/", incomplete_user_data)
    # проверка статуса ответа
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    required_fields = ['password' , 'region']
    for fields in required_fields:
        assert fields in response.data , f"Field '{fields}' should be required" 


# Проверка на то что пользователь не может создать пользователя
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

    # отправка тестовых данных на эндпоинт
    response = api_client.post("/user/create/", user_data)
    # Проверка статуса ответа
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Проверка на то что пользователь не может залогинеться если логин совпадает с логином другого пользователя
@pytest.mark.django_db
def test_create_user_with_existing_login(authenticated_client):
     # Создаем пользователя с определённым login
    existing_user_data = {
        "login": "duplicateuser",
        "password": "securepassword123",
        "name": "John",
        "surname": "Doe",
        "is_staff": False,
        "is_active": True,
        "region": "Чуйская",
        "role": "user",
    }
    authenticated_client.post("/user/create/", existing_user_data)
    # Пытаемся создать второго пользователя с тем же login
    response = authenticated_client.post("/user/create/", existing_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "login" in response.data, "Поле 'login' должно возвращать ошибку"
    assert "already exists" in response.data["login"][0], "Сообщение об ошибке должно содержать 'already exists'"

