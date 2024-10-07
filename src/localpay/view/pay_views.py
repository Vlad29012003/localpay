from rest_framework.views import APIView
from localpay.models import User_mon, Pays
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from localpay.permission import IsUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class Payment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    async def clinet_payment(self, ls, payment_amount, user_login):

        user_data = User_mon.objects.filter(login=user_login).first()
        user_id = user_data.id
        user_balance = user_data.balance
        user_avail_balance = user_data.avail_balance
        user_access = user_data.access

        ls = int(ls)
        payment_amount = float(payment_amount)
        current_time = datetime.now()
        service_id_hydra = current_time.strftime("%Y%m%d%H%M%S")
        txn_date = str(current_time)[:-4]
        txn_id = service_id_hydra + str(ls)

        if int(user_balance) < int(payment_amount) or not user_access:
            return HttpResponse('У вас недостаточно средств для оплаты или отсутствует доступ к оплате')

        payment_url = (
            f'http://pay.snt.kg:9080/localpayskynet_osmp/main?command=pay&txn_id={txn_id}'
            f'&txn_date={service_id_hydra}&account={ls}&sum={payment_amount}'
        )

        async with httpx.AsyncClient() as client:
            payment_response = await client.post(payment_url)
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
        except Exception:
            soup = BeautifulSoup(payment_response.text, features="xml")
            transaction_id = soup.find('osmp_txn_id').string
            transaction_sum = soup.find('sum').string
            payment_status = soup.find('result').string
            result = {
                'transaction_id': transaction_id,
                'sum': transaction_sum,
                'status': payment_status
            }

        if payment_status == '0':
            payment_status_desc = 'Выполнен'
            payment_record = Pays.objects.create(
                number_payment=transaction_id, date_payment=txn_date,
                accept_payment=response_time, ls_abon=ls,
                money=transaction_sum, status_payment=payment_status_desc, user_id=user_id
            )
            payment_record.save()

        transaction_sum_int = int(str(transaction_sum)[:-2])
        if payment_status == '0':
            updated_balance = int(user_balance) - transaction_sum_int
            updated_avail_balance = int(user_avail_balance) - transaction_sum_int

            user_data.balance = updated_balance
            user_data.avail_balance = updated_avail_balance
            user_data.save(update_fields=['balance', 'avail_balance'])

        return JsonResponse(result)
