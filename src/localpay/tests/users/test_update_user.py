import pytest
from rest_framework import status
from localpay.models import User_mon , Pays, Comment

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        defaults = {
            "login": "default_user",
            "password": "default_password",
            "name": "Default",
            "surname": "User",
            "balance": 0.0,
            "avail_balance": 0.0,
            "role": "user",
            "is_active": True,
        }
        defaults.update(kwargs)
        user = User_mon.objects.create(**defaults)
        return user
    return make_user



# Проверка обновления полей пользователя
def test_update_existing_user(authenticated_client, create_user):
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        balance=100.0,
        avail_balance=50.0,
    )
    # обновление полей  login , password , region
    updated_data = {
        "name": "Updated",
        "surname": "User",
        "role": "admin",
        "login": user.login,
        "password": user.password,
        "region": user.region,
    }
    # Отправляем тестовый запрос на обновление
    response = authenticated_client.put(f"/users/{user.id}/update_user/", updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Updated"
    assert response.data["role"] == "admin"



# Проверка обновления несуществующего пользователя
@pytest.mark.django_db
def test_update_non_existing_user(authenticated_client):
    updated_data = {
        "name": "Nonexistent",
    }
    # обновление пользователя с ID 999
    response = authenticated_client.put(f"/users/999/update_user/", updated_data)
    
    # Проверяем отправку статуса
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "User not found"


# Проверка на пополнения баланса пользователю 
@pytest.mark.django_db
# Создаю пользователя
def test_refill_balance(authenticated_client, create_user):
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        balance=100.0,
        avail_balance=50.0,
        region="Чуйская", 
    )

    # Пополняею баланс
    updated_data = {
        "refill": 50.0,
        "comment": "Пополнение баланса",
        "login": user.login,
        "password": user.password,
        "region": user.region,
        "write_off": 0.0
    }
    # Отправляю тестовые данные на эндпоинт
    response = authenticated_client.put(f"/users/{user.id}/update_user/", updated_data)

    # Проверка статуса
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.balance == 150.0

    # Проверка комментария "Пополнение баланса"
    comment = Comment.objects.filter(user2=user).last()
    assert comment.text == "Пополнение баланса"
    assert comment.old_balance == 100.0
    assert comment.new_balance == 50.0
    assert comment.mont_balance == 150.0



# Проверка на списание для существующего пользователя
@pytest.mark.django_db
def test_write_off_exceeding_balance(authenticated_client, create_user):
    # Создаем пользователя
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        avail_balance=10.0,
        region="Чуйская", 
        balance=100.0,
    )

    # Пытаемся списать больше, чем доступный баланс
    updated_data = {
        "write_off": 60.0,
        "comment": "Списание средств",
        "login": user.login,
        "password": user.password,
        "region": user.region,
    }
    response = authenticated_client.put(f"/users/{user.id}/update_user/", updated_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert any(
        "Сумма списания не может быть больше затрат" in error
        for error in response.data
    )
