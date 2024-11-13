from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from localpay.models import Comment
from localpay.serializers.comments_serializer.comments_serializer import CommentSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from localpay.permission import  IsAdmin , IsSupervisor


class CommentsList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin , IsSupervisor]
    def get(self , request , *args , **kwargs):
        comments = Comment.objects.all().order_by('-created_at')
        serializer = CommentSerializer(comments , many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)