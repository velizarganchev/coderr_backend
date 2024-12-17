from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
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

        business_user = validated_data.get('business_user')

        if not business_user:
            raise serializers.ValidationError(
                {'error': 'business_user is required'})

        if Review.objects.filter(business_user=business_user, reviewer=user):
            raise serializers.ValidationError(
                {
                    'error': 'Sie haben dieses Unternehmen bereits bewertet'
                })

        review = Review.objects.create(reviewer=user, **validated_data)
        return review

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviewer'] = instance.reviewer.id
        return representation
