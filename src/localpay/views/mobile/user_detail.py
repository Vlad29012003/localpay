
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.models import User_mon
from localpay.serializers.user import UserSerializer
from localpay.permission import IsUser
import logging

mobile_detail_user_logger = logging.getLogger('detail_view_user')
mobile_detail_handler = logging.FileHandler('user_detail.log')  
mobile_detail_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
mobile_detail_handler.setFormatter(formatter)
mobile_detail_user_logger.addHandler(mobile_detail_handler)
mobile_detail_user_logger.setLevel(logging.INFO)


# Detail Payment for user
class MobileUserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsUser]
    def get(self, request, user_id):
        try:
            user = User_mon.objects.get(pk=user_id)
        except User_mon.DoesNotExist:

            mobile_detail_user_logger.info(f'user with this {user_id} cant see this detail page')

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)

        mobile_detail_user_logger.info(f'User {user} watch her detail information')
        return Response(serializer.data)