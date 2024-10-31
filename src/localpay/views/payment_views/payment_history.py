from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.permission import IsSupervisor , IsAdmin
from localpay.models import Pays , User_mon 
from localpay.serializers.payment_serializers.payment_history_serializer import PaymentHistorySerializer
from localpay.schema.swagger_schema import search_param
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from .logging_config import payment_logger


# List of payment history (Only for admin and supervisor)
class PaymentHistoryListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = PaymentHistorySerializer

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        queryset = Pays.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(ls_abon__icontains=search_query) |  
                Q(user__login__icontains=search_query)|
                Q(user__name__icontains = search_query)|
                Q(user__surname__icontains = search_query)
            )

        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            queryset = queryset.filter(date_payment__lte=datetime.fromisoformat(date_to))

        total_count = queryset.count()

        queryset = queryset.order_by('-date_payment')

        payment_logger.info(f"User {request.user.login} {request.user.login} requested payment history with search {search_query} Date from {date_from}, Date to {date_to}. Total count {total_count}")


        page_size = int(request.query_params.get('page_size', 50))
        page_number = request.GET.get('page', 1)

        paginator = Paginator(queryset, page_size)

        try:
            payments = paginator.page(page_number)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(payments, many=True)

        return Response({
            'count': total_count,  
            'total_pages': paginator.num_pages,  
            'page_size': page_size, 
            'current_page': page_number,  
            'results': serializer.data, 
        }, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Pays.objects.all()
    


# Payment history User only for Admin 
class UserPaymentHistoryListAPIView(PaymentHistoryListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User_mon.objects.get(id=user_id)
        except User_mon.DoesNotExist:
            return Pays.objects.none()

        return Pays.objects.filter(user=user)

    def list(self, request, user_id):  
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        queryset = self.get_queryset()

        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            queryset = queryset.filter(date_payment__lte=datetime.fromisoformat(date_to))

        if search_query:
            queryset = queryset.filter(
                Q(ls_abon__icontains=search_query) |
                Q(status_payment__icontains=search_query)
            )

        total_count = queryset.count()

        payment_logger.info(f"User {request.user.login} {request.user.login} request user payment history search {search_query} Date from {date_from} , Date to {date_to} Total count {total_count}")

        page_size = int(request.query_params.get('page_size', 50))
        page_number = request.GET.get('page', 1)

        paginator = Paginator(queryset, page_size)

        try:
            payments = paginator.page(page_number)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(payments, many=True)

        return Response({
            'count': total_count,
            'total_pages': paginator.num_pages,
            'page_size': page_size,
            'current_page': page_number,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)
