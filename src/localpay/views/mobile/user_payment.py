from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from localpay.permission import IsUser
from localpay.models import Pays
from localpay.models import User_mon
from localpay.views.payment_views.payment_history import PaymentHistoryListAPIView
from .logging_config import mobile_detail_user_logger

class MobileUserPaymentHistoryListAPIView(PaymentHistoryListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    def get_queryset(self):
        user = self.request.user  # Получаем пользователя из токена
        try:
            mobile_detail_user_logger.info(f'User {user.id} found for payments history request')
        except User_mon.DoesNotExist:
            mobile_detail_user_logger.warning(f'User with ID {user.id} not found.')
            return Pays.objects.none()

        return Pays.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()

        if total_count == 0:
            mobile_detail_user_logger.info(f'No payments found for user with ID {request.user.id}.')

        mobile_detail_user_logger.info(f'Payment history for user with ID {request.user.id} contains {total_count} records.')

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'count': total_count,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)
