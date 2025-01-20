from rest_framework import serializers
from .models import Post, Follower, UserAction
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at']


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['follower', 'following']


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ['user', 'target_user', 'action']
