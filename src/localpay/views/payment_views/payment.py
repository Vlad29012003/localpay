from rest_framework.generics import CreateAPIView , UpdateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer , PaymentUpdateSerializer
from localpay.permission import IsUser ,  IsAdmin
from localpay.models import Pays
import json
from asgiref.sync import async_to_sync
from .logging_config import payment_logger

# Create payment only for user 
class PaymentCreateAPIView(CreateAPIView):
    permission_classes= [IsUser]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = async_to_sync(serializer.process_payment)()

            # log successful payment
            success_message = {'Message':f'Payment create for User {request.user.id} Result {result}'}
            payment_logger.info(json.dumps(success_message))
            return Response(result, status=status.HTTP_200_OK)
        
        # log payment validation errors
        error_message = {'Message':f'Payment creation failed for User ID {request.user.id} Errors {serializer.errors}'}
        payment_logger.warning(json.dumps(error_message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update payment (only for admin)
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

            # log update suscessfull payment
            success_message = {'Message':f'Payment update suscessful for User {request.user.id}'}
            payment_logger.info(json.dumps(success_message))
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # log failed payment update
        error_message = {'Message':f'Failed to update Payment for user {request.user.id} Error {serializer.errors}'}
        payment_logger.warning(json.dumps(error_message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)