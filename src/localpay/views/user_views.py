from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
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
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




class UserListAndCreateAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = UserSerializer

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')

        if search_query:
            queryset = User_mon.objects.filter(
                Q(name__icontains=search_query) |
                Q(surname__icontains=search_query) |
                Q(login__icontains=search_query)
            )
        else:
            queryset = User_mon.objects.all()

        total_count = queryset.count()

    
        page_size = int(request.query_params.get('page_size', 50))  
        page_number = request.GET.get('page', 1)

        paginator = Paginator(queryset, page_size)

        try:
            users = paginator.page(page_number)  
        except PageNotAnInteger:
 
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(users, many=True)

        return Response({
            'count': total_count, 
            'total_pages': paginator.num_pages,  
            'page_size': page_size,  
            'current_page': page_number, 
            'results': serializer.data,
        }, status=status.HTTP_200_OK)


class UserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    permission_classes= [IsAdmin|IsSupervisor]
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
    
