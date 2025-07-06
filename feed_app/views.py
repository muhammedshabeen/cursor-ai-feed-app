from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Post
from .serializers import PostSerializer, UserRegistrationSerializer, UserSerializer, LoginSerializer
from .utils import calculate_post_score, mark_post_as_seen, get_optimized_user_feed

# Create your views here.

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            return Response({
                'token': token.key,
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)
            return Response({
                'message': 'User registered successfully!',
                'user': user_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkPostSeenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        mark_post_as_seen(request.user, post)
        return Response({
            'message': f'Post {post_id} marked as seen',
            'post_id': post_id
        }, status=status.HTTP_200_OK)

class FeedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Validate parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        # Get optimized feed with pagination
        result = get_optimized_user_feed(
            user=request.user,
            page=page,
            page_size=page_size,
            use_cache=True
        )
        
        # Serialize posts with scores
        post_data = []
        for post in result['posts']:
            # Calculate score for display (could be cached)
            score = calculate_post_score(request.user, post)
            serializer = PostSerializer(post)
            data = serializer.data
            data['score'] = round(score, 2)
            post_data.append(data)
        
        # Prepare response with pagination info
        response_data = {
            'posts': post_data,
            'pagination': result['pagination']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
