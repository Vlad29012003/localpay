from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'  # Указываем, что используем login вместо username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'] = serializers.CharField()
        self.fields['password'] = serializers.CharField()
        
        # Удаляем поле username, если оно присутствует
        if 'username' in self.fields:
            del self.fields['username']

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        

        if not login or not password:
            raise serializers.ValidationError(_('Both login and password are required.'))

        # Добавляем username в attrs для совместимости с родительским классом
        attrs['username'] = login

        try:
            user = User.objects.get(login=login)
            if not user.check_password(password):
                raise serializers.ValidationError(_('Invalid login or password.'))

            # Установим правильного пользователя для валидации
            self.user = user

        except User.DoesNotExist:
            raise serializers.ValidationError(_('Invalid login or password.'))

        # После проверки возвращаем результат
        data = super().validate(attrs)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['login'] = user.login
        token['role'] = user.role
        return token
