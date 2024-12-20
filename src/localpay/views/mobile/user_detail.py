
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.models import User_mon
from localpay.serializers.user import UserSerializer
from localpay.permission import IsUser
import json
from .logging_config import mobile_detail_user_logger


# Detail Payment for user
class MobileUserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    def get(self, request):
        user = request.user  # Получаем пользователя из токена

        try:
            user_instance = User_mon.objects.get(pk=user.id)
        except User_mon.DoesNotExist:

            error_message = {'Message':f'User with ID {user.id} not found.'}
            mobile_detail_user_logger.info(json.dumps(error_message))

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user_instance)

        info_message = {'Message':f'User {user_instance} accessed their detail information.'}
        mobile_detail_user_logger.info(json.dumps(info_message))
        return Response(serializer.data)
