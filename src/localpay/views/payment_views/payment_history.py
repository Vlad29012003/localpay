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
from drf_yasg.utils import swagger_auto_schema
from localpay.schema.swagger_schema import search_param
from django.db.models import Q
from datetime import datetime



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
                Q(user__login__icontains=search_query)
            )

        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            queryset = queryset.filter(date_payment__lte=datetime.fromisoformat(date_to))

        total_count = queryset.count()


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