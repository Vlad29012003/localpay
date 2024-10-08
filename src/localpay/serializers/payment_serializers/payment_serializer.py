from asgiref.sync import sync_to_async
from rest_framework import serializers
from localpay.models import User_mon, Pays
from datetime import datetime
import httpx
from bs4 import BeautifulSoup


class PaymentSerializer(serializers.Serializer):
    ls = serializers.IntegerField()
    payment_amount = serializers.FloatField()
    user_login = serializers.CharField(max_length=255)

    async def process_payment(self):
        ls = self.validated_data['ls']
        payment_amount = self.validated_data['payment_amount']
        user_login = self.validated_data['user_login']

        user_data = await sync_to_async(User_mon.objects.filter(login=user_login).first)()  # Await DB query
        user_id = user_data.id
        user_balance = user_data.balance
        user_avail_balance = user_data.avail_balance
        user_access = user_data.access

        current_time = datetime.now()
        service_id_hydra = current_time.strftime("%Y%m%d%H%M%S")
        txn_date = str(current_time)[:-4]
        txn_id = service_id_hydra + str(ls)

        if int(user_balance) < int(payment_amount) or not user_access:
            return {'error': 'Insufficient balance or no access'}

        payment_url = (
            f'http://pay.snt.kg:9080/localpayskynet_osmp/main?command=pay&txn_id={txn_id}'
            f'&txn_date={service_id_hydra}&account={ls}&sum={payment_amount}'
        )

        async with httpx.AsyncClient() as client:
            payment_response = await client.post(payment_url)  # Await the HTTP request
            payment_response.encoding = 'utf-8'

        response_time = str(datetime.now())[:-4]

        try:
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
            soup = BeautifulSoup(payment_response.text, features="xml")
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
