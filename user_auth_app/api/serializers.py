from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from user_auth_app.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['pk',
                  'username', 'first_name', 'last_name', 'email', 'token', 'date_joined']

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    """
    user = serializers.CharField(source='user.id')
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    created_at = serializers.DateTimeField(source='user.date_joined')

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name',
                  'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return instance


class UserProfileTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model filtered by type.
    """
    user = UserSerializer()
    uploaded_at = serializers.DateTimeField(source='user.date_joined')

    class Meta:
        model = UserProfile
        fields = ['user', 'file', 'location', 'tel',
                  'description', 'working_hours', 'type', 'uploaded_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.type == 'customer':
            return {
                'user': representation['user'],
                'file': representation['file'],
                'uploaded_at': representation['uploaded_at'],
                'type': representation['type']
            }
        return representation
