from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async, async_to_sync
from localpay.models import Pays, User_mon
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer


class PaymentHistoryListAPIView(ListAPIView):
    serializer_class = PaymentHistorySerializer

    def get(self, request, *args, **kwargs):
        user_login = request.query_params.get('user_login')

        if not user_login:
            return Response({'error': 'User login required'}, status=status.HTTP_400_BAD_REQUEST)

        user = async_to_sync(User_mon.objects.filter(login=user_login).first)()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        payments = async_to_sync(lambda: list(Pays.objects.filter(user_id=user.id).order_by('-date_payment')))()

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
