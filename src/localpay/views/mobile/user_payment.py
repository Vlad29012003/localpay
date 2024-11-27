from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from localpay.permission import IsUser
from localpay.models import Pays
from localpay.models import User_mon
from localpay.views.payment_views.payment_history import PaymentHistoryListAPIView
from .logging_config import mobile_detail_user_logger
import json
from datetime import datetime


class MobileUserPaymentHistoryListAPIView(PaymentHistoryListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    def get_queryset(self):
        user = self.request.user
        try:
            info_message = {'Message':f'User {user.id} found for payments history request'}
            mobile_detail_user_logger.info(json.dumps(info_message))

        except User_mon.DoesNotExist:

            error_message = {'Message':f'User with ID {user.id} not found.'}
            mobile_detail_user_logger.warning(json.dumps(error_message))
            return Pays.objects.none()
        
        now = datetime.now()
        start_of_month = now.replace(day=1)
        end_of_month = now.replace(month=now.month % 12 + 1 , day=1) if now.month < 12 else now.replace(month=1, year=now.year + 1)

        return Pays.objects.filter(user=user ,created_at__gte=start_of_month, created_at__lt=end_of_month )

    def list(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()

        if total_count == 0:

            error_message = {'Message':f'No payments found for user with ID {request.user.id}.'}
            mobile_detail_user_logger.info(json.dumps(error_message))

        info_message = {f'Payment history for user with ID {request.user.id} contains {total_count} records.'}
        mobile_detail_user_logger.info(json.dumps(info_message))

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'count': total_count,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)
