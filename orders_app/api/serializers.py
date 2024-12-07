from rest_framework import serializers
from ..models import Order, Feature


class OrderSerializer(serializers.ModelSerializer):
    features = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Feature.objects.all())

    class Meta:
        model = Order
        fields = ['customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']
