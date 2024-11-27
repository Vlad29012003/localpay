import pytest
from rest_framework import status
from localpay.models import User_mon
from rest_framework.test import APIClient


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


# Проверка успешного создания Платежа
@pytest.mark.django_db
def test_create_payment_success(authenticated_user_client):
    user = User_mon.objects.filter(login="user").first()
    if user:
        user.balance = 1000.0 
        user.avail_balance = 1000.0
        user.access = True 
        user.save()

    # Данные платежа
    payment_data = {
        "ls": 175050620,
        "login": "user",
        "money": 50.0,
        "service_type": "test_service",
        "comment": "Test payment",
    }

    response = authenticated_user_client.post("/api/create-payment/", payment_data)

    assert response.status_code == status.HTTP_200_OK
    assert "transaction_id" in response.data
    assert "sum" in response.data
    assert "status" in response.data
    assert response.data["status"] == "0"



# Проверка платежа с недостаточным балансом
@pytest.mark.django_db
def test_create_payment_insufficient_balance(authenticated_client, create_user):
    user = create_user(
        login="testuser",
        password="password123",
        name="Test",
        surname="User",
        avail_balance=20.0,
        region="Чуйская",
        balance=30.0,
        role="user",
    )

    payment_data = {
        "ls": 12345,
        "login": "testuser",
        "money": 50.0,
        "service_type": "test_service",
        "comment": "Test payment",
    }

    response = authenticated_client.post("/api/create-payment/", payment_data)

    # Проверяем, код ошибки
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == "You do not have permission to perform this action."

