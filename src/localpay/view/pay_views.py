from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from localpay.models import Pays, User_mon
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer
from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    async def service_engineer_payment(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = await serializer.process_payment()
            return result
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ls = int(ls)
        payment_amount = float(payment_amount)
        current_time = datetime.now()
        service_id_hydra = current_time.strftime("%Y%m%d%H%M%S")
        txn_date = str(current_time)[:-4]
        txn_id = service_id_hydra + str(ls)

    @action(detail=False, methods=['get'])
    def payment_history(self, request):
        user_login = request.query_params.get('user_login')

        if not user_login:
            return Response({'error': 'User login required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User_mon.objects.filter(login=user_login).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        payments = Pays.objects.filter(user_id=user.id).order_by('-date_payment')

        serializer = PaymentHistorySerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
