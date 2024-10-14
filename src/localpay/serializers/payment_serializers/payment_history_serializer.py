from rest_framework import serializers
from localpay.models import Pays
from rest_framework.pagination import PageNumberPagination


class PaymentHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()  

    class Meta:
        model = Pays
        fields = ['number_payment', 'date_payment', 'accept_payment', 'ls_abon', 'money', 'status_payment' , 'user_name']

    def get_user_name(self, obj):
        return f"{obj.user.name} {obj.user.surname}"

