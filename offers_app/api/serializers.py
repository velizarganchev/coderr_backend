from rest_framework import serializers
from ..models import Offer, OfferDetail, Feature


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['name']


class OfferDetailSerializer(serializers.ModelSerializer):
    features = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Feature.objects.all())

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    user_details = serializers.SerializerMethodField('get_user_details_field')

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            features = detail_data.pop('features')
            offer_detail = OfferDetail.objects.create(
                offer=offer, **detail_data)
            offer_detail.features.set(features)
        return offer

    # def get_details_field(self, obj):
    #     """
    #     Retrieves a list of details associated with the given object.

    #     Args:
    #         obj: The object containing the details.

    #     Returns:
    #         A list of dictionaries, each containing the 'id' and 'url' of a detail.
    #     """
    #     return [{"id": detail.id, "url": f"/offerdetails/{detail.id}/"} for detail in obj.details.all()]

    def get_user_details_field(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }
