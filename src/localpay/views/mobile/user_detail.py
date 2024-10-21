
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.models import User_mon
from localpay.serializers.user import UserSerializer
from localpay.permission import IsUser


class MobileUserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsUser]
    def get(self, request, user_id):
        try:
            user = User_mon.objects.get(pk=user_id)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)