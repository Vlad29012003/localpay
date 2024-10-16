from rest_framework import serializers
from localpay.models import Pays
from rest_framework.pagination import PageNumberPagination


class PaymentHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    planup_id = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Pays
        fields = ['number_payment', 'date_payment', 'accept_payment', 'ls_abon', 'money', 'status_payment' , 'user_name' , 'planup_id' , 'user_id']

    def get_user_name(self, obj):
        return f"{obj.user.name} {obj.user.surname}"
   
    def get_planup_id(self, obj):
        return obj.user.planup_id
    
    def get_user_id(self, obj):
        return obj.user.id

