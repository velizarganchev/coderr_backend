from rest_framework import serializers
from rest_framework.authtoken.models import Token
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['reviewer']

    def create(self, validated_data):
        """
        Create a new review instance.
        """
        request = self.context.get('request')

        token_key = None
        if request:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Token '):
                token_key = auth_header.split(' ')[1]

        if not token_key:
            raise serializers.ValidationError({'error': 'Token is required'})

        try:
            user = Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            raise serializers.ValidationError({'error': 'Invalid token'})

        business_user = validated_data.get('business_user')
        if not business_user:
            raise serializers.ValidationError(
                {'error': 'The business_user field is required.'}
            )

        if Review.objects.filter(business_user=business_user, reviewer=user).exists():
            raise serializers.ValidationError(
                {'error': 'You have already reviewed this business.'}
            )

        review = Review.objects.create(reviewer=user, **validated_data)
        return review
