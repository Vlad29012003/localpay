from asgiref.sync import async_to_sync
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer

class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = async_to_sync(serializer.process_payment)()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
