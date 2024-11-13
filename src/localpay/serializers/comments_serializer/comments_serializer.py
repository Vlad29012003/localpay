from rest_framework import serializers
from localpay.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user2 = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format='%d %B %Y г. %H:%M', read_only =True)

    class Meta:
        model = Comment
        fields = ['user2', 'text', 'type_pay', 'old_balance', 'new_balance', 'mont_balance', 
                  'old_avail_balance', 'new_avail_balance', 'mont_avail_balance', 'created_at']