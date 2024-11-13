from rest_framework import serializers
from localpay.models import User_mon , Pays , Comment
from django.contrib.auth.hashers import make_password
from datetime import datetime

from rest_framework import serializers
from django.utils import timezone
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_mon
        fields = [
            'id', 'name', 'surname', 'login', 'password', 'access', 
            'balance', 'avail_balance', 'region', 'date_reg', 
            'refill', 'write_off', 'comment', 'role', 'is_active', 'planup_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'date_reg': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password']) 
        validated_data['date_reg'] = timezone.now()  

        if 'role' not in validated_data:
            validated_data['role'] = 'user'

        return super().create(validated_data)

    # def validate_write_off(self, value):
    #     """
    #     Проверяем, что значение списания является положительным числом
    #     """
    #     try:
    #         write_off = float(value)
    #         if write_off <= 0:
    #             raise serializers.ValidationError(
    #                 "Сумма списания должна быть положительным числом"
    #             )
    #     except (ValueError, TypeError):
    #         raise serializers.ValidationError(
    #             "Сумма списания должна быть числом"
    #         )
    #     return value


    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'password':
                instance.password = make_password(value)
            elif field == 'refill':
                try:
                    refill_amount = float(value)
                    instance.balance += refill_amount
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        "Сумма пополнения должна быть числом"
                    )
            elif field == 'write_off':
                try:
                    write_off_amount = float(value)
                    # Проверяем, что списание не больше абсолютного значения затрат
                    if write_off_amount > abs(instance.avail_balance):
                        raise serializers.ValidationError(
                            "Сумма списания не может быть больше затрат"
                        )

                    # Увеличиваем баланс на сумму списания
                    instance.balance += write_off_amount
                    # Уменьшаем затраты (делаем их ближе к нулю)
                    instance.avail_balance += write_off_amount

                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        "Сумма списания должна быть числом"
                    )
            else:
                setattr(instance, field, value)

        instance.save()
        return instance



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'text', 'type_pay', 'old_balance', 'new_balance', 
            'mont_balance', 'old_avail_balance', 'new_avail_balance', 
            'mont_avail_balance', 'created_at'
        ]



class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = [
            'number_payment', 'date_payment', 'accept_payment', 
            'ls_abon', 'money', 'status_payment', 'user', 
            'annulment', 'document_number', 'comment']

