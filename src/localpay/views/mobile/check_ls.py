from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from localpay.serializers.payment_serializers.payment_serializer import  check_ls
from localpay.serializers.payment_serializers.payment_serializer import AccountCheckSerializer


class AccountCheckView(APIView):
    def post(self, request):
        serializer = AccountCheckSerializer(data=request.data)
        if serializer.is_valid():
            ls = serializer.validated_data['ls']
            result = check_ls(ls)
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)