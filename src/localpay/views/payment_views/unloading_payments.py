from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime, timedelta
from localpay.models import Pays , User_mon
from localpay.permission import IsAdmin
import requests
import decimal


class CombinedPaymentComparisonView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user_id = request.data.get('user_id')
        search_query = request.data.get('search', '')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')

        if not date_from or not date_to:
            date_from = None
            date_to = None
            return Response({"error": "date_from и date_to обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        all_localpay_payments = self.get_localpay_payments(request, date_from, date_to, user_id=user_id)
        all_planup_payments = self.get_planup_payments([user_id] if user_id else None, date_from, date_to)

        comparison_report = self.compare_payments(all_localpay_payments, all_planup_payments)

        return Response({
            'count': len(comparison_report),
            'results': comparison_report,
        }, status=status.HTTP_200_OK)

    
    def get_localpay_payments(self, request, date_from, date_to, user_id=None):
        queryset = Pays.objects.all()
        
        if user_id:
            queryset = queryset.filter(user__id=user_id)


        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            date_to_inclusive = datetime.fromisoformat(date_to) + timedelta(days=1)
            queryset = queryset.filter(date_payment__lt=date_to_inclusive)

        return queryset

    def get_planup_payments(self, user_ids, start_date, end_date):
        planup_payments = []

        if user_ids is None:
            user_ids = User_mon.objects.values_list('id', flat=True)

        for user_id in user_ids:
            try:
                user = User_mon.objects.get(id=user_id)
                planup_id = user.planup_id
                planup_url = "http://planup.skynet.kg:8000/planup/localpay_naryd/"
                data = {"planup_id": planup_id, "start_date": start_date, "end_date": end_date}

                response = requests.post(planup_url, data=data)
                if response.status_code != 200:
                    print(f"Не удалось получить данные из Planup для пользователя {user_id}. Код статуса: {response.status_code}")
                    continue

                user_payments = response.json()
                planup_payments.extend([
                    {
                        "user_id": user_id,
                        "ls_abon": p["ls_abon"],
                        "money": self.parse_money(p["money"]),
                        "planup_id": p['id'],
                        "end_date": p.get('end_date')
                    }
                    for p in user_payments if self.parse_money(p["money"]) != 0
                ])
            except Exception as e:
                print(f"Ошибка при получении платежей из Planup для пользователя {user_id}: {str(e)}")

        return planup_payments

    def parse_money(self, money_str):
        try:
            return int(decimal.Decimal(money_str) * 100)
        except (ValueError, decimal.InvalidOperation):
            return 0

    def compare_payments(self, localpay_payments, planup_payments):
        report = {}
        localpay_total = 0      
        planup_total = 0

        print(localpay_payments)
        print(111111111111111111111111111111111111111111)
        print(planup_payments)

        # Обработка платежей LocalPay
        for payment in localpay_payments:
            user_id = payment.user.id
            ls_abon = payment.ls_abon
            money = self.parse_money(payment.money)
            localpay_total += money

            if user_id not in report:
                user = User_mon.objects.get(id=user_id)
                report[user_id] = {
                    "user_id": user_id,
                    "name": user.name,
                    "surname": user.surname,
                    "payments": [],
                    "localpay_total": 0,
                    "planup_total": 0
                }


            report[user_id]["payments"].append({
                "ls_abon": ls_abon,
                "localpay_money": self.format_money(money),
                "planup_money": "ТАКОЙ ОТСУТСВУЕТ В PLANUP",
                "status_payment": payment.status_payment,
                "date_payment": payment.date_payment ,
                "end_date": None,
                "planup_id": None
            })
            report[user_id]["localpay_total"] += money

        # Обработка платежей PlanUp
        for payment in planup_payments:
            user_id = payment["user_id"]
            ls_abon = payment["ls_abon"]
            money = payment["money"]
            planup_total += money

            if user_id not in report:
                user = User_mon.objects.get(id=user_id)
                report[user_id] = {
                    "user_id": user_id,
                    "name": user.name,
                    "surname": user.surname,
                    "payments": [],
                    "localpay_total": 0,
                    "planup_total": 0
                }

            matching_payment = next((p for p in report[user_id]["payments"] if p["ls_abon"] == ls_abon and p["localpay_money"] == self.format_money(money)), None)

            if matching_payment:
                matching_payment["planup_money"] = self.format_money(money)
                matching_payment["planup_id"] = payment["planup_id"]
            else:
                report[user_id]["payments"].append({
                    "ls_abon": ls_abon,
                    "localpay_money": "ПЛАТЕЖ ОТСУТСВУЕТ В LOCALPAY",
                    "planup_money": self.format_money(money),
                    "status_payment": None,
                    "date_payment": None,
                    "end_date": payment["end_date"],
                    "planup_id": payment["planup_id"]
                })

            report[user_id]["planup_total"] += money

        # Преобразование словаря отчета в список и добавление итогов
        report_list = list(report.values())
        report_list.append({
            "user_id": "Итого",
            "name": "",
            "surname": "",
            "payments": [],
            "localpay_total": self.format_money(localpay_total),
            "planup_total": self.format_money(planup_total)
        })

        return report_list

    def format_money(self, cents):
        return f"{cents / 100:.2f}"