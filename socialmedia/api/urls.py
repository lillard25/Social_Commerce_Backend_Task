from django.urls import path
from . import views
from .views import RegisterView, PostListView, FollowView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name="register"),
    path('posts/', PostListView.as_view(), name="posts"),
    path('users/<str:username>/follow/', FollowView.as_view(), name="follow"),
    path('users/<str:username>/followers/', views.list_followers, name='list_followers'),
    path('users/<str:username>/following/', views.list_following, name='list_following'),
    path('users/<str:username>/action/', views.hide_block_user, name='hide_block_user'),
    path('users/<str:username>/delete_action/', views.remove_action, name='remove_action'),  # Handle DELETE
    path('users/actions/', views.list_hidden_blocked, name='list_hidden_blocked'),
    path('feed/', views.user_feed, name='user_feed'),
]
