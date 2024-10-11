from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from localpay.permission import IsUser , IsSupervisor , IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async, async_to_sync
from localpay.models import Pays, User_mon
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer



class PaymentHistoryListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]

    serializer_class = PaymentHistorySerializer

    def get(self, request, *args, **kwargs):
        payments = Pays.objects.all().order_by('-date_payment')
        
        if not payments:
            return Response({'error': 'No payment records found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)