from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from localpay.permission import IsUser
from localpay.models import Pays
from localpay.models import User_mon
from datetime import datetime
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from localpay.views.payment_views.payment_history import PaymentHistoryListAPIView

class MobileUserPaymentHistoryListAPIView(PaymentHistoryListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User_mon.objects.get(id=user_id)
        except User_mon.DoesNotExist:
            return Pays.objects.none()

        return Pays.objects.filter(user=user)

    def list(self, request, user_id):
        queryset = self.get_queryset()

        total_count = queryset.count()

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'count': total_count,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)

