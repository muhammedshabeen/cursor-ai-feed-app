from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Post, Interest, UserProfile

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class PostSerializer(serializers.ModelSerializer):
    tags = InterestSerializer(many=True, read_only=True)
    score = serializers.FloatField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'text', 'image', 'tags', 'created_at', 'score']

class UserSerializer(serializers.ModelSerializer):
    primary_interests = InterestSerializer(many=True, read_only=True)
    secondary_interests = InterestSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email','primary_interests', 'secondary_interests']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Must include username and password.")

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    primary_interests = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of interest IDs for primary interests"
    )
    secondary_interests = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        help_text="List of interest IDs for secondary interests (optional)"
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_primary_interests(self, value):
        # Check if all primary interest IDs exist
        existing_ids = set(Interest.objects.filter(id__in=value).values_list('id', flat=True))
        if len(existing_ids) != len(value):
            missing_ids = set(value) - existing_ids
            raise serializers.ValidationError(f"Interest IDs {missing_ids} do not exist.")
        return value

    def validate_secondary_interests(self, value):
        if value:
            # Check if all secondary interest IDs exist
            existing_ids = set(Interest.objects.filter(id__in=value).values_list('id', flat=True))
            if len(existing_ids) != len(value):
                missing_ids = set(value) - existing_ids
                raise serializers.ValidationError(f"Interest IDs {missing_ids} do not exist.")
        return value

    def create(self, validated_data):
        # Extract interest data
        primary_interest_ids = validated_data.pop('primary_interests')
        secondary_interest_ids = validated_data.pop('secondary_interests', [])
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Get user profile (should be created automatically by signals)
        profile = user.profile
        
        # Set interests
        primary_interests = Interest.objects.filter(id__in=primary_interest_ids)
        secondary_interests = Interest.objects.filter(id__in=secondary_interest_ids)
        
        profile.primary_interests.set(primary_interests)
        profile.secondary_interests.set(secondary_interests)
        
        return user 