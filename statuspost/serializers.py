from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'image', 'caption', 'created_at',
            'likes_count', 'comments_count'
        ]

    def validate(self, data):
        if not data.get('image'):
            raise ValidationError({"image": "Image is required to create a post."})
        return data

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()
        if not data.get('caption'):
            raise ValidationError({"caption": "Caption cannot be empty."})