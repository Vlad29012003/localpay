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



class PaymentHistoryListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = PaymentHistorySerializer

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')

        if search_query:
            queryset = Pays.objects.filter(
                Q(ls_abon__icontains=search_query) |  
                Q(user__login__icontains=search_query) 
            )
        else:
            queryset = Pays.objects.all()

        total_count = queryset.count()

        page_size = int(request.query_params.get('page_size', 50))
        page_number = request.GET.get('page', 1)
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = self.get_serializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def get_queryset(self):
        return Pays.objects.all()