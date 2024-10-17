from rest_framework import serializers
from localpay.models import User_mon , Pays
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
            'refill', 'write_off', 'comment', 'role' , 'is_active','planup_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'date_reg': {'read_only': True},
            # 'balance': {'read_only': True},
            # 'avail_balance': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password']) 
        validated_data['date_reg'] = timezone.now()  

        if 'role' not in validated_data:
            validated_data['role'] = 'user'

        return super().create(validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'password':
                instance.password = make_password(value)
            else:
                setattr(instance, field, value)
        instance.save()
        return instance





class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = [
            'number_payment', 'date_payment', 'accept_payment', 
            'ls_abon', 'money', 'status_payment', 'user', 
            'annulment', 'document_number', 'comment']


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Ты че пароли же не совпадают")
        return attrs
    
