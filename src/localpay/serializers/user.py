from rest_framework import serializers
from localpay.models import User_mon , Pays , Comment
from django.contrib.auth.hashers import make_password
from datetime import datetime
from localpay.serializers.comments_serializer.comments_serializer import CommentSerializer

from rest_framework import serializers
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    region = serializers.ChoiceField(choices=User_mon.REGION_CHOICES, required=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = User_mon
        fields = [
            'id', 'name', 'surname', 'login', 'password', 'access', 
            'balance', 'avail_balance', 'region', 'date_reg', 
            'refill', 'write_off', 'comment', 'role', 'is_active', 'planup_id' , 'comments'
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


    def update(self, instance, validated_data):
        old_balance = instance.balance
        old_avail_balance = instance.avail_balance
        comment_text = validated_data.pop('comment', None)


        for field, value in validated_data.items():
            print(f'{field}  -   {value}')
            if field == 'password':
                instance.password = make_password(value)
            elif field == 'refill'and float(value) > 0:
                try:
                    refill_amount = float(value)
                    write_off_amount = float(validated_data['write_off'])
                    instance.balance += refill_amount

                    time = str(datetime.now())[:-4]
                    status_payment = 'Пополнение с бухгалтерии'
                    ls = '*********'
                    check_pay = Pays.objects.create(user=instance,date_payment=time,accept_payment=time,ls_abon=ls,money=refill_amount, status_payment=status_payment)
                    check_pay.save() 

                    # Сохраняем операцию пополнения в истории
                    Comment.objects.create(
                        user2=instance,
                        text=comment_text if comment_text else "Пополнение баланса",
                        type_pay="Пополнение",
                        old_balance=old_balance,
                        new_balance=refill_amount,  # Сумма пополнения
                        mont_balance=instance.balance, # Текущий баланс
                        old_avail_balance=old_avail_balance,
                        new_avail_balance=write_off_amount,
                        mont_avail_balance=instance.avail_balance,
                        created_at=timezone.now()
                    )
                    instance.save()
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        "Сумма пополнения должна быть числом"
                    )
            elif field == 'write_off' and float(value) > 0:
                try:
                    write_off_amount = float(value)
                    if write_off_amount > abs(instance.avail_balance):
                        raise serializers.ValidationError(
                            "Сумма списания не может быть больше затрат"
                        )
                    old_avail_balance = instance.avail_balance
                    instance.balance += write_off_amount
                    instance.avail_balance += write_off_amount
                    # Сохраняем операцию списания в истории

                    time = str(datetime.now())[:-4]
                    status_payment = 'Списание с бухгалтерии'
                    ls = '*********'
                    check_pay = Pays.objects.create(user=instance,date_payment=time,accept_payment=time,ls_abon=ls,money=write_off_amount, status_payment=status_payment)
                    check_pay.save() 


                    Comment.objects.create(
                        user2=instance,
                        text=comment_text if comment_text else "Списание средств",
                        type_pay="Списание",
                        old_balance=old_balance,
                        new_balance=write_off_amount,
                        mont_balance=instance.balance, # Текущий баланс
                        old_avail_balance=old_avail_balance, # Сумма списания
                        new_avail_balance=write_off_amount,
                        mont_avail_balance=instance.avail_balance,
                        created_at=timezone.now()
                    )
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



class RegionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()