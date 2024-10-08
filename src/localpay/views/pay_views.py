# from rest_framework.viewsets import ViewSet
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.decorators import action
# from localpay.models import Pays, User_mon
# from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer
# from localpay.serializers.payment_serializers.payment_serializer import PaymentSerializer
# from asgiref.sync import sync_to_async
#
#
# class PaymentViewSet(ViewSet):
#     @action(detail=False, methods=['post'])
#     async def service_engineer_payment(self, request, *args, **kwargs):
#         if getattr(self, 'swagger_fake_view', False):
#             # Prevent schema generation errors
#             return Response()
#
#         serializer = PaymentSerializer(data=request.data)
#         if serializer.is_valid():
#             # Await the async process_payment method
#             result = await serializer.process_payment()
#             return Response(result, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=False, methods=['get'])
#     async def payment_history(self, request):
#         user_login = request.query_params.get('user_login')
#
#         if not user_login:
#             return Response({'error': 'User login required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Use sync_to_async to make the query awaitable
#         user = await sync_to_async(User_mon.objects.filter(login=user_login).first)()
#         if not user:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         # Retrieve payment history and await the query
#         payments = await sync_to_async(lambda: list(Pays.objects.filter(user_id=user.id).order_by('-date_payment')))()
#
#         serializer = PaymentHistorySerializer(payments, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
