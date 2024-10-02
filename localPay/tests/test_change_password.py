import unittest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, Mock

client = TestClient(app)

class TestPasswordChange(unittest.TestCase):

    @patch('routers.user_router.get_user_service')  # Убедитесь, что путь правильный
    def test_successful_change_password(self, mock_get_user_service):
        # Создаем мок для сервиса пользователя
        user_service_mock = Mock()
        user_service_mock.change_password.return_value = None
        mock_get_user_service.return_value = user_service_mock

        # Отправляем запрос на изменение пароля
        response = client.post('/users/246/change-password', json={
            "new_password": "55555555",
            "confirm_password": "55555555"
        })

        # Проверяем, что ответ успешен
        assert response.status_code == 200
        assert response.json() == {'message': 'Password changed successfully'}

        # Проверяем, что метод change_password был вызван с правильными аргументами
        user_service_mock.change_password.assert_called_once_with(246, mock.ANY, mock.ANY)


    # def test_password_didnt_happen(self):
    #     user_service_mock = Mock()

    #     with patch('routers.user_router.get_user_service', return_value=user_service_mock):
    #         response = client.post('/users/246/change-password', json={
    #             "new_password": "55555555",
    #             "confirm_password": "55555553"
    #         })

    #         assert response.status_code == 400
    #         assert response.json() == {'detail': 'Passwords do not match'}

    #         user_service_mock.change_password.assert_not_called()

    # def test_password_user_not_exist(self):
    #     user_service_mock = Mock()

    #     user_service_mock.change_password.side_effect = ValueError("User not found")

    #     with patch('routers.user_router.get_user_service', return_value=user_service_mock):
    #         response = client.post('/users/246/change-password', json={
    #             "new_password": "new_password123",
    #             "confirm_password": "new_password123"
    #         })

    #         assert response.status_code == 404
    #         assert response.json() == {"detail": "User not found"}
