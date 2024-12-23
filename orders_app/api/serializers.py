from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied

from offers_app.models import OfferDetail, Feature
from ..models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'offer_type', 'status', 'features',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['customer_user', 'business_user', 'title', 'revisions',
                            'delivery_time_in_days', 'price', 'offer_type', 'features']

    @staticmethod
    def get_current_user_from_request(context):
        """
        Helper function to extract and validate the user from the request.
        """
        request = context.get('request')
        if not request:
            raise serializers.ValidationError(
                {'error': 'Request context fehlt.'}
            )

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            raise serializers.ValidationError(
                {'error': 'Token ist erforderlich'}
            )

        token_key = auth_header.split(' ')[1]
        try:
            return Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            raise serializers.ValidationError({'error': 'Ungültiges Token'})

    def create(self, validated_data):
        """
        Create a new order instance.
        """
        customer_user = self.get_current_user_from_request(self.context)

        if customer_user.userprofile.type == 'business':
            raise serializers.ValidationError(
                {'error': 'Nur Kunden können Bestellungen aufgeben'}
            )

        offer_detail_id = self.context['request'].data.get('offer_detail_id')
        if not offer_detail_id:
            raise serializers.ValidationError(
                {'error': 'offer_detail_id is required'}
            )

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                {'error': 'Invalid offer_detail_id'}
            )

        business_user = offer_detail.offer.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            offer_type=offer_detail.offer_type
        )
        order.features.set(offer_detail.features.all())
        return order

    def update(self, instance, validated_data):
        """
        Update an existing order instance.
        """
        current_user = self.get_current_user_from_request(self.context)

        if current_user != instance.business_user:
            raise PermissionDenied(
                {'error': 'Nur der Business-Benutzer kann den Status aktualisieren'}
            )

        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Customize the representation of the order instance.
        """
        representation = super().to_representation(instance)
        representation['features'] = [
            feature.name for feature in instance.features.all()]
        return representation
