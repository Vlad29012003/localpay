from rest_framework import serializers
from localpay.models import Pays

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ['number_payment', 'date_payment', 'accept_payment', 'ls_abon', 'money', 'status_payment']
