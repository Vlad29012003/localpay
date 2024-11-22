import pytest
from rest_framework import status
from localpay.models import User_mon , Pays
from rest_framework.test import APIClient



# Аунтефикация пользователя
@pytest.fixture
def authenticated_user_client(db):
    admin_user = User_mon.objects.create_user(
        login="user",
        password="userpassword",
        name="User",
        surname="User",
        avail_balance=100.0,
        region="user Region", 
        balance=1000.0,
        role="user"
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


@pytest.mark.django_db
def test_create_payment_success(authenticated_user_client):
    # Убедитесь, что пользователь имеет достаточно средств и доступ
    user = User_mon.objects.filter(login="user").first()
    if user:
        user.balance = 1000.0  # Установите достаточный баланс
        user.avail_balance = 1000.0
        user.access = True    # Обеспечьте доступ
        user.save()

    # Данные платежа
    payment_data = {
        "ls": 175050620,
        "login": "user",  # Логин аутентифицированного пользователя
        "money": 50.0,
        "service_type": "test_service",
        "comment": "Test payment",
    }

    # Отправляем запрос на создание платежа
    response = authenticated_user_client.post("/api/create-payment/", payment_data)

    # Проверяем, что запрос был успешным
    assert response.status_code == status.HTTP_200_OK
    assert "transaction_id" in response.data
    assert "sum" in response.data
    assert "status" in response.data
    assert response.data["status"] == "0"

