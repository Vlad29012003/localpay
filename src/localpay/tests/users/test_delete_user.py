import pytest
from rest_framework import status
from localpay.models import User_mon
from rest_framework.test import APIClient

# Аунтефикация пользователя
@pytest.fixture
def authenticated_admin_client(db):
    admin_user = User_mon.objects.create_user(
        login="admin",
        password="adminpassword",
        name="Admin",
        surname="User",
        avail_balance=100.0,
        region="Admin Region", 
        balance=1000.0,
        role="admin"
    )
    
    client = APIClient()
    client.force_authenticate(user=admin_user)
    
    return client


# Создаем пользователя 
@pytest.fixture
def create_user():
    def _create_user(login, password, name, surname, avail_balance, region, balance, role):
        return User_mon.objects.create_user(
            login=login,
            password=password,
            name=name,
            surname=surname,
            avail_balance=avail_balance,
            region=region,
            balance=balance,
            role=role
        )
    return _create_user



# Проверка на то что админ может удальть пользователя
@pytest.mark.django_db
def test_delete_user_success(authenticated_admin_client, create_user):
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        avail_balance=10.0,
        region="Чуйская", 
        balance=100.0,
        role="user",
    )


    response = authenticated_admin_client.delete(f"/user/{user.id}/delete_user/")

    # Проверяем статус удаления
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что пользователя больше нет в базе данных
    assert not User_mon.objects.filter(id=user.id).exists()


# Проверка удаление несуществующего пользователя
@pytest.mark.django_db
def test_delete_user_not_found(authenticated_admin_client):
    response = authenticated_admin_client.delete("/user/9999/delete_user/")

    # Проверяем, код ошибки 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Not found"


# Проверка на удаления пользователя без прав администратора 
@pytest.mark.django_db
def test_delete_user_permission_denied(authenticated_client, create_user):
    # Создаем пользователя
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        avail_balance=10.0,
        region="Чуйская", 
        balance=100.0,
        role="user",
    )

    # Попытка обычного пользователя удалить другого пользователя
    response = authenticated_client.delete(f"/user/{user.id}/delete_user/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data is None


# Попытка удалить пользователя без аутентификации
@pytest.mark.django_db
def test_delete_user_unauthorized(client, create_user):
    # Создаем пользователя
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        avail_balance=10.0,
        region="Чуйская", 
        balance=100.0,
        role='user'
    )

    response = client.delete(f"/user/{user.id}/delete_user/")

    # Проверяем,код ошибки 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
