from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from localpay.models import User_mon
from localpay.serializers.user import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from localpay.schema.swagger_schema import search_param
from django.db.models import Q
from localpay.serializers.user import ChangePasswordSerializer
from localpay.permission import IsUser , IsSupervisor , IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserListAndCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsAdmin|IsSupervisor]
    @swagger_auto_schema(manual_parameters=[search_param])
    def get(self, request):
        search_query = request.query_params.get('search', '')

        if search_query:
            users = User_mon.objects.filter(
                Q(name__icontains=search_query) |
                Q(surname__icontains=search_query) |
                Q(login__icontains=search_query)
            )
        else:
            users = User_mon.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)



class UserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsAdmin|IsSupervisor]
    pagination_class = StandardResultsSetPagination
    def get(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    


class ChangePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsAdmin]
    def post(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            user.password = make_password(new_password)
            user.save()
            return Response({"success": "Пароль успешно изменен."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def put(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CreateUserAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def delete(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        user = User_mon.objects.get(pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            user.password = make_password(new_password)
            user.save()
            return Response({"success": "о четко брат (братюня)."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
