from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from localpay.permission import IsUser , IsSupervisor , IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async, async_to_sync
from localpay.models import Pays, User_mon
from localpay.serializers.user import UserSerializer , PaysSerializer
from rest_framework.pagination import PageNumberPagination
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




class PaymentHistoryListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = PaymentHistorySerializer


    def get_queryset(self):
        return Pays.objects.all()

    def get(self, request, *args, **kwargs):
        payments = Pays.objects.all()

        total_payments = payments.count()

        page_size = int(request.query_params.get('page_size', 50)) 
        page_number = request.GET.get('page', 1)
        paginator = Paginator(payments, page_size) 

        try:
            payment = paginator.page(page_number)  
        except PageNotAnInteger:

            payment = paginator.page(1)
        except EmptyPage:
            payment = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(payment, many=True)

        return Response({
            'count':total_payments,
            'total_pages': paginator.num_pages,
            'page_size': page_size,
            'current_page': page_number, 
            'results': serializer.data,
            }, status=status.HTTP_200_OK)
