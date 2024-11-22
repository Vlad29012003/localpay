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
from datetime import datetime , timedelta , time
from .logging_config import payment_logger
import json
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50  # количество элементов на странице по умолчанию
    limit_query_param = 'limit'  # параметр запроса для установки лимита
    offset_query_param = 'offset'  # параметр запроса для установки смещения

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,               # Общее количество элементов
            'limit': self.get_limit(self.request),    # Лимит (количество элементов на порцию)
            'offset': self.get_offset(self.request),  # Текущее смещение
            'results': data,                   # Данные текущей порции
        })

class PaymentHistoryListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = PaymentHistorySerializer
    pagination_class = CustomLimitOffsetPagination  # Используем наш класс пагинации на основе смещения и лимита

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        queryset = Pays.objects.all()

        # Фильтрация по поисковому запросу
        if search_query:
            search_parts = search_query.split()
            if len(search_parts) == 2:
                name_query, surname_query = search_parts
                queryset = queryset.filter(
                    Q(user__name__icontains=name_query) & Q(user__surname__icontains=surname_query)
                )
            else:
                queryset = queryset.filter(
                    Q(ls_abon__icontains=search_query) |
                    Q(user__login__icontains=search_query) |
                    Q(user__name__icontains=search_query) |
                    Q(user__surname__icontains=search_query)
                )

        # Фильтрация по датам
        if date_from:
            queryset = queryset.filter(date_payment__gte=datetime.fromisoformat(date_from))
        if date_to:
            # Если date_payment - это DateTimeField, включаем конечный день целиком
            date_to_obj = datetime.fromisoformat(date_to) + timedelta(days=1)
            date_to_end_of_day = datetime.combine(date_to_obj, time.max)
            queryset = queryset.filter(date_payment__lte=date_to_end_of_day)

        queryset = queryset.order_by('-date_payment')

        # Количество всех записей
        total_count = queryset.count()

        # Логирование
        info_message = {
            "Message": f"User {request.user.login} requested payment history with search '{search_query}' "
                       f"Date from {date_from}, Date to {date_to}. Total count {total_count}"
        }
        payment_logger.info(json.dumps(info_message))

        # Применяем встроенную пагинацию DRF на основе смещения и лимита
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Если пагинация не применяется (например, когда количество объектов меньше, чем limit), возвращаем все данные
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Pays.objects.all()
    
