from asgiref.sync import sync_to_async
from rest_framework import serializers
from localpay.models import User_mon, Pays , Comment
from datetime import datetime 
import httpx 
from django.utils import timezone

from bs4 import BeautifulSoup
import requests


async def check_ls(ls):
    url = f'http://pay.snt.kg:9080/localpayskynet_osmp/main?command=check&account={ls}'
    print(f'Запрос к {url}')
    
    try:
        x = requests.post(url)
        x.encoding = 'utf-8'
        print(f'Ответ сервера: {x.text}')

        soup = BeautifulSoup(x.text, features="xml")
        abon = soup.find('fio').string if soup.find('fio') else 'Не указано'
        status = soup.find('result').string if soup.find('result') else 'Нет статуса'
        
        print(f'Найден абонент: {abon}, статус: {status}')
        return {'fio': abon, 'status': status}
    
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при запросе: {str(e)}')
        return {'error': 'Ошибка при обращении к серверу'}



class PaymentSerializer(serializers.Serializer):
    ls = serializers.IntegerField()
    login = serializers.CharField(max_length=255)
    money = serializers.FloatField()
    service_type = serializers.CharField(max_length=100)
    comment = serializers.CharField(max_length=255, required=False)

    async def process_payment(self):
        ls = self.validated_data['ls']
        money = self.validated_data['money']
        login = self.validated_data['login']
        service_type = self.validated_data.get('service_type')
        comment = self.validated_data.get('comment', '')


        account_check_result = await check_ls(ls)
        if account_check_result['status'] != '0':
            return {'error': 'Неверный лицевой счет или статус: ' + account_check_result.get('comment', '')}

        user_data = await sync_to_async(User_mon.objects.filter(login=login).first)()
        if not user_data:
            return {'error': 'Пользователь не найден'}

        user_id = user_data.id

        
        user_balance = user_data.balance

        user_avail_balance = user_data.avail_balance
        user_access = user_data.access

        if user_balance < money or not user_access:
            return {'error': 'Недостаточно средств или отсутствует доступ'}

        current_time = datetime.now()
        service_id_hydra = current_time.strftime("%Y%m%d%H%M%S")
        txn_date = str(current_time)[:-4]
        txn_id = service_id_hydra + str(ls)

        # URL для платежа
        payment_url = (
            f'http://pay.snt.kg:9080/localpayskynet_osmp/main?command=pay&txn_id={txn_id}'
            f'&txn_date={service_id_hydra}&account={ls}&sum={money}'
        )

        async with httpx.AsyncClient() as client:
            payment_response = await client.post(payment_url)
            payment_response.encoding = 'utf-8'

        response_time = str(datetime.now())[:-4]

        try:
            # Парсинг XML ответа
            soup = BeautifulSoup(payment_response.text, features="xml")
            transaction_id = soup.find('osmp_txn_id').string
            comment = soup.find('comment').string
            transaction_sum = soup.find('sum').string
            payment_status = soup.find('result').string
            result = {
                'transaction_id': transaction_id,
                'sum': transaction_sum,
                'comment': comment,
                'status': payment_status
            }
        except Exception as e:
            soup = BeautifulSoup(payment_response.text, 'lxml')
            transaction_id = soup.find('osmp_txn_id').string
            transaction_sum = soup.find('sum').string
            payment_status = soup.find('result').string
            result = {
                'transaction_id': transaction_id,
                'sum': transaction_sum,
                'status': payment_status,
                'error': str(e)
            }

        if payment_status == '0':
            payment_status_desc = 'Выполнен'
            await sync_to_async(Pays.objects.create)(
                number_payment=transaction_id, date_payment=txn_date,
                accept_payment=response_time, ls_abon=ls,
                money=transaction_sum, status_payment=payment_status_desc, user_id=user_id
            )

            transaction_sum_int = int(str(transaction_sum)[:-2])
            user_data.balance -= transaction_sum_int
            user_data.avail_balance -= transaction_sum_int
            await sync_to_async(user_data.save)(update_fields=['balance', 'avail_balance'])

        return result


class AccountCheckSerializer(serializers.Serializer):
    ls = serializers.IntegerField()


class PaymentUpdateSerializer(serializers.ModelSerializer):
    annulment = serializers.BooleanField()

    class Meta:
        model = Pays
        fields = ['annulment']

    def update_balance(self, instance):
        user_data = User_mon.objects.get(id=instance.user.id)
        print(user_data)

        if instance.annulment != True:

            transaction_sum_float = float(instance.money)
            transaction_sum_int = int(transaction_sum_float)  

            old_balance = user_data.balance
            old_avail_balance = user_data.avail_balance


            print(f"Transaction Sum (int): {transaction_sum_int}")
            print(f"User Balance before: {user_data.balance}")
            print(f"User Available Balance before: {user_data.avail_balance}")

            user_data.balance += transaction_sum_int
            user_data.avail_balance += transaction_sum_int
            user_data.save()

            Comment.objects.create(
                user2=user_data,
                text="Аннулирование платежа",
                type_pay="Аннулирование",
                old_balance=old_balance,

                new_balance=transaction_sum_int,

                
                mont_balance=user_data.balance,
                old_avail_balance=old_avail_balance,
                new_avail_balance=transaction_sum_int,
                mont_avail_balance=user_data.avail_balance,
                created_at=timezone.now()
            )



            print(f"User Balance after: {user_data.balance}")  
            print(f"User Available Balance after: {user_data.avail_balance}")  

            user_data.save()  

            instance.annulment = True 
            instance.save() 
        else:
            print('123456789')
        return instance

    def update(self, instance, validated_data): 

        instance = self.update_balance(instance)
        return instance

