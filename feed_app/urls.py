from django.urls import path
from . import views

app_name = 'feed_app'

urlpatterns = [
    path('api/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/feed/', views.FeedAPIView.as_view(), name='feed'),
    path('api/posts/<int:post_id>/seen/', views.MarkPostSeenAPIView.as_view(), name='mark_post_seen'),
]