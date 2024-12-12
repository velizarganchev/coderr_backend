from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        request = self.context.get('request')
        token_key = None
        user = None
        if request:
            auth_header = request.headers.get('Authorization')
            if auth_header and ' ' in auth_header:
                token_key = auth_header.split(' ')[1]

        if not token_key:
            raise serializers.ValidationError(
                {'error': 'Token ist erforderlich'})

        try:
            user = Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            raise serializers.ValidationError({'error': 'Ungültiges Token'})

        if user.userprofile.type == 'customer':
            if Review.objects.filter(reviewer=user.userprofile).exists():
                raise serializers.ValidationError(
                    {
                        'error': 'Sie haben dieses Unternehmen bereits bewertet'
                    })

        business_user = validated_data.get('business_user')

        if not business_user:
            raise serializers.ValidationError(
                {'error': 'business_user is required'})

        validated_data.pop('reviewer', None)
        review = Review.objects.create(
            reviewer=user.userprofile, **validated_data)
        return review

    
        