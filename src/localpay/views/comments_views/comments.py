from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from localpay.models import Comment
from localpay.serializers.comments_serializer.comments_serializer import CommentSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.permission import  IsAdmin , IsSupervisor
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, timedelta, time
from rest_framework.generics import ListAPIView
from django.db.models import Q


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'limit': self.get_limit(self.request),
            'offset': self.get_offset(self.request),
            'results': data,
        })


class CommentsList(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = CommentSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        queryset = Comment.objects.all()

        if search_query:
            queryset = queryset.filter(user2__name__icontains=search_query)


        if date_from:
            queryset = queryset.filter(created_at__gte=datetime.fromisoformat(date_from))
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to) + timedelta(days=1)
            date_to_end_of_day = datetime.combine(date_to_obj, time.max)
            queryset = queryset.filter(created_at__lte=date_to_end_of_day)

        return queryset.order_by('-created_at')