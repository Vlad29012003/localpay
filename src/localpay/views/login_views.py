from rest_framework_simplejwt.views import TokenObtainPairView
from localpay.serializers.login import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
