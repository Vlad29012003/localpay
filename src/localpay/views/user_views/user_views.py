from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from localpay.models import User_mon
from localpay.serializers.user import UserSerializer
from localpay.schema.swagger_schema import search_param
from localpay.serializers.user import ChangePasswordSerializer
from localpay.permission import IsUser , IsSupervisor , IsAdmin
import logging
from drf_yasg.utils import swagger_auto_schema

user_logger = logging.getLogger('user_actions')
user_handler = logging.FileHandler('users.log')  
user_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
user_handler.setFormatter(formatter)
user_logger.addHandler(user_handler)
user_logger.setLevel(logging.INFO)




class UserDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsUser|IsAdmin|IsSupervisor]
    def get(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)



# Views for create user (unly admin)
class CreateUserAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            user_logger.info(f'User create {serializer.validated_data.get("login")} by admin {request.user.login}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        user_logger.warning(f'Failed to create user. Errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Views for update user (only admin)
class UpdateUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def put(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:

            user_logger.error(f'cant find a user with this {pk}')
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_logger.info(f'successfully update user with id {user.pk}')
            return Response(serializer.data)
        
        user_logger.info(f'Failed to update user with id {user.pk} . Error: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Views for delete users (only admin)
class DeleteUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def delete(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            user_logger.error(f'User with this {pk} not found')

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        user_logger.info(f'successfully deleate a user with id {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)


# list of all users (for admin and supervisor)
class UserListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = UserSerializer

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')
        user_logger.info(f'User {request.user.login} is requesting user list with search query: "{search_query}"')

        # search for name surname and login
        if search_query:
            queryset = User_mon.objects.filter(
                Q(name__icontains=search_query) |
                Q(surname__icontains=search_query) |
                Q(login__icontains=search_query)
            )
            user_logger.info(f'Search user {search_query} returned {queryset.count()} result')
        else:
            # take all users
            queryset = User_mon.objects.all()
            user_logger.info(f'No Search user send all users')

        # pagination 
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


# Change password for user (only admin)
class ChangePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsAdmin]
    def post(self, request, pk):
        user_logger.info(f'Admin {request.user.login} is trying to change password for user ID {pk}.')

        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:

            user_logger.warning(f'User in this {pk} not found found by admin {request.user.login}')
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            user.password = make_password(new_password)
            user.save()
            user_logger.info(f'Suscessfully change a password for user {user.pk} by admin {request.user.login}')
            return Response({"success": "Пароль успешно изменен."}, status=status.HTTP_200_OK)

        user_logger.error(f'Cant change a password for user {user.pk} by admin {request.user.login}. Errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    


    
