from asgiref.sync import async_to_sync
import requests
from rest_framework.generics import CreateAPIView , UpdateAPIView 
from rest_framework.response import Response
from rest_framework import status
from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer , PaymentUpdateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.models import Pays , User_mon
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from localpay.views.payment_views.payment_history import PaymentHistoryListAPIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from localpay.permission import IsAdmin
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer


class PaymentService:
    def get_user_payments(self, user_login , start_date , end_date):
        try:
            user = User_mon.objects.get(login=user_login)
        except User_mon.DoesNotExist:
            raise ValueError(f"User with login '{user_login}' not found")

        payments = Pays.objects.filter(user=user)

        if start_date:
            payments = payments.filter(date_payment__gte=start_date)
        if end_date:
            payments = payments.filter(date_payment__lte=end_date)

        payments = payments.filter(money__gt=0)
        return payments


class UserPaymentHistoryListAPIView(PaymentHistoryListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User_mon.objects.get(id=user_id)
        except User_mon.DoesNotExist:
            return Pays.objects.none()

        return Pays.objects.filter(user=user)

    def list(self, request, user_id):  
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        queryset = self.get_queryset()

        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            queryset = queryset.filter(date_payment__lte=datetime.fromisoformat(date_to))

        if search_query:
            queryset = queryset.filter(
                Q(ls_abon__icontains=search_query) |
                Q(status_payment__icontains=search_query)
            )

        total_count = queryset.count()

        page_size = int(request.query_params.get('page_size', 50))
        page_number = request.GET.get('page', 1)

        paginator = Paginator(queryset, page_size)

        try:
            payments = paginator.page(page_number)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(payments, many=True)

        return Response({
            'count': total_count,
            'total_pages': paginator.num_pages,
            'page_size': page_size,
            'current_page': page_number,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)


class PlanupLocalpayCompareAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request):
        print("Получен запрос:", request.data)
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        planup_id = request.data.get('planup_id') 

        if not planup_id:
            return Response({"error": "Необходим planup_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(f"Пытаемся найти платежи с planup_id={planup_id}")
            planup_url = f"http://planup.skynet.kg:8000/planup/localpay_naryd/"
            data = {"planup_id": planup_id}
            if start_date:
                data["start_date"] = start_date
            if end_date:
                data["end_date"] = end_date

            response = requests.post(planup_url, data=data)
            if response.status_code != 200:
                raise Exception(f"Не удалось получить данные из Planup. Код статуса: {response.status_code}")

            planup_payments = response.json()
            print(f"Полученные платежи из Planup: {planup_payments}")
            planup_payments = [
                {
                    "ls_abon": p["ls_abon"],
                    "money": int(p["money"]) if isinstance(p["money"], str) and p["money"].isdigit() and int(p["money"]) != 0 else 0
                }
                for p in planup_payments if isinstance(p["money"], str) and p["money"].isdigit() and int(p["money"]) != 0
            ]

            report = []
            planup_total = sum(p['money'] for p in planup_payments)

            for payment in planup_payments:
                ls_abon = payment['ls_abon']
                money = payment['money']
                report.append({
                    "ls_abon": ls_abon,
                    "planup_money": money
                })
            report.append({
                "ls_abon": "Итого",
                "planup_money": planup_total
            })

            return Response({
                "report": report
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
