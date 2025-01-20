from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Post, Follower, UserAction
from .serializers import PostSerializer, UserActionSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)


class PostListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        author_username = request.query_params.get('author')
        posts = Post.objects.all()
        if author_username:
            author = get_object_or_404(User, username=author_username)
            posts = posts.filter(author=author)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        if request.user == target_user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        if Follower.objects.filter(follower=request.user, following=target_user).exists():
            return Response({"error": "Already following."}, status=status.HTTP_400_BAD_REQUEST)
        Follower.objects.create(follower=request.user, following=target_user)
        return Response({"message": f"You are now following {username}."})

    def delete(self, request, username):
        target_user = get_object_or_404(User, username=username)
        follow_instance = Follower.objects.filter(follower=request.user, following=target_user).first()
        if not follow_instance:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)
        follow_instance.delete()
        return Response({"message": f"You have unfollowed {username}."})

# List Followers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_followers(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    followers = Follower.objects.filter(following=user)
    follower_users = [f.follower for f in followers]
    return Response([user.username for user in follower_users], status=status.HTTP_200_OK)


# List Following
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_following(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    following = Follower.objects.filter(follower=user)
    following_users = [f.following for f in following]
    return Response([user.username for user in following_users], status=status.HTTP_200_OK)


# Hide/Block User
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hide_block_user(request, username):
    action = request.data.get("action")
    if action not in ['HIDE', 'BLOCK']:
        return Response({"error": "Invalid action. Choose 'HIDE' or 'BLOCK'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.user == target_user:
        return Response({"error": "You cannot hide/block yourself."}, status=status.HTTP_400_BAD_REQUEST)

    # Check for existing action (HIDE or BLOCK) for the target user by the current user
    if UserAction.objects.filter(user=request.user, target_user=target_user, action=action).exists():
        return Response({"error": f"Duplicate {action.lower()}s are not allowed."}, status=status.HTTP_400_BAD_REQUEST)

    # Create UserAction instance
    user_action, created = UserAction.objects.get_or_create(user=request.user, target_user=target_user)
    user_action.action = action
    user_action.save()

    return Response({"message": f"User {action.lower()}d successfully."}, status=status.HTTP_201_CREATED)


# Remove Hide/Block Action
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_action(request, username):
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        user_action = UserAction.objects.get(user=request.user, target_user=target_user)
        user_action.delete()
        return Response({"message": "Action removed successfully."}, status=status.HTTP_200_OK)
    except UserAction.DoesNotExist:
        return Response({"error": "No action found."}, status=status.HTTP_404_NOT_FOUND)


# List Hidden/Blocked Users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_hidden_blocked(request):
    actions = UserAction.objects.filter(user=request.user)
    action_users = [action.target_user.username for action in actions]
    return Response(action_users, status=status.HTTP_200_OK)


# Get User Feed (with Hide/Block logic)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    # Get the users the logged-in user is following
    following = Follower.objects.filter(follower=request.user)
    following_users = [f.following for f in following]

    # Get hidden or blocked users
    blocked_users = UserAction.objects.filter(user=request.user, action='BLOCK').values_list('target_user', flat=True)
    hidden_users = UserAction.objects.filter(user=request.user, action='HIDE').values_list('target_user', flat=True)

    # Filter posts from the following users but exclude hidden and blocked users
    posts = Post.objects.filter(author__in=following_users).exclude(author__in=blocked_users)

    # Remove posts from hidden users
    posts = posts.exclude(author__in=hidden_users)

    # Serialize posts and return them
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

