from asgiref.sync import async_to_sync
from rest_framework.generics import CreateAPIView , UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer , PaymentUpdateSerializer
from localpay.permission import IsUser , IsSupervisor , IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.models import Pays

class PaymentCreateAPIView(CreateAPIView):
    permission_classes= [IsUser]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = async_to_sync(serializer.process_payment)()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class PaymentUpdateAPIView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    serializer_class = PaymentUpdateSerializer
    queryset = Pays.objects.all()

    def update(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.update(instance, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)