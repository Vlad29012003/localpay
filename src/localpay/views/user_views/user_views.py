from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from localpay.models import User_mon 
from localpay.serializers.user import UserSerializer , RegionSerializer
from localpay.schema.swagger_schema import search_param
from localpay.permission import IsUser , IsSupervisor , IsAdmin
from .logging_config import user_logger
import json
from drf_yasg.utils import swagger_auto_schema




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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            log_data = {
                "action": "create_user",
                "created_user": serializer.validated_data.get("login"),
                "admin": request.user.login
            }
            user_logger.info(json.dumps(log_data))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        log_data = {
            "action": "create_user_failed",
            "errors": serializer.errors,
            "admin": request.user.login
        }
        user_logger.warning(json.dumps(log_data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



# Views for update user (only admin)
class UpdateUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def put(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:

            error_message = {"message": f"Can't find a user with this ID: {pk}"}
            user_logger.error(json.dumps(error_message))

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            success_message = {"Message": f"Successfully updated user with ID: {user.pk}"}
            user_logger.info(json.dumps(success_message))
            return Response(serializer.data)
        
        error_message = {"Message": f'Failed to update user with id {user.pk}' ,"Error": serializer.errors}
        user_logger.info(json.dumps(error_message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Views for delete users (only admin)
class DeleteUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    def delete(self, request, pk):
        try:
            user = User_mon.objects.get(pk=pk)
        except User_mon.DoesNotExist:
            error_message = {"message": "User with this {pk} not found"}
            user_logger.info(json.dumps(error_message))

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        success_message = {"Message":f'successfully deleate a user with id {pk}'}
        user_logger.info(json.dumps(success_message))
        return Response(status=status.HTTP_204_NO_CONTENT)


# list of all users (for admin and supervisor)
class UserListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSupervisor]
    serializer_class = UserSerializer

    @swagger_auto_schema(manual_parameters=[search_param])
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '').strip()
        fields = ['name', 'surname', 'login']


        info_message = {"Message":f'User {request.user.login} is requesting user list with search query:' ,"SearchQuery":list(search_query)}
        user_logger.info(json.dumps(info_message))

        queryset = User_mon.search_manager.search(query=search_query, fields=fields)

        # search for name surname and login
        # if search_query:
        #     queryset = User_mon.objects.filter(
        #         Q(name__icontains=search_query) |
        #         Q(surname__icontains=search_query) |
        #         Q(login__icontains=search_query)
        #     )
        #     info_messager = {"Message":f'Search user {search_query} returned {queryset.count()} result'}
        #     user_logger.info(json.dumps(info_messager))
        # else:
        #     # take all users
        #     queryset = User_mon.objects.all()
        #     error_message = {"Message":f'No Search user send all users'}
        #     user_logger.info(json.dumps(error_message))
            

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




class RegionListView(APIView):
    def get(self, request):
        regions = [{"value": choice[0], "label": choice[1]} for choice in User_mon.REGION_CHOICES]
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)
