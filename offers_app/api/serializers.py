from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from ..models import Offer, OfferDetail, Feature

OFFER_DETAIL_FIELDS = ['revisions',
                       'delivery_time_in_days', 'price', 'offer_type']


class FeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Feature model.
    """
    class Meta:
        model = Feature
        fields = ['name']

    def to_internal_value(self, data):
        """
        Overrides the default method to create a Feature if it doesn't exist.
        """
        feature, created = Feature.objects.get_or_create(name=data)
        return feature


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the OfferDetail model.
    """
    features = FeatureSerializer(many=True)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']

    def create(self, validated_data):
        features_data = validated_data.pop('features', [])
        offer_detail = OfferDetail.objects.create(**validated_data)

        features = [
            Feature.objects.get_or_create(
                name=feature.get('name', '').strip())[0]
            # Skip invalid entries
            for feature in features_data if feature.get('name')
        ]
        offer_detail.features.set(features)
        return offer_detail

    def update(self, instance, validated_data):
        features_data = validated_data.pop('features', [])
        instance = super().update(instance, validated_data)

        features = [
            Feature.objects.get_or_create(
                name=feature.get('name', '').strip())[0]
            for feature in features_data if feature.get('name')
        ]
        instance.features.set(features)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Transform `features` field
        features_representation = [
            feature.name for feature in instance.features.all()]
        representation['features'] = features_representation

        return representation


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for the Offer model.
    """
    user = serializers.ReadOnlyField(source='user.username')
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
        request = self.context.get('request')
        token_key = request.headers.get('Authorization').split(' ')[
            1] if request else None
        user = Token.objects.get(key=token_key).user if token_key else None
        details_data = validated_data.pop('details', [])

        if user.userprofile.type != 'business':
            raise serializers.ValidationError(
                {'error': 'Nur Geschäftskunden können Angebote erstellen'})

        offer = Offer.objects.create(user=user, **validated_data)

        min_price = None
        min_delivery_time = None

        for detail_data in details_data:
            features_data = detail_data.pop('features')
            offer_detail = OfferDetail.objects.create(
                offer=offer, **detail_data)

            features = [
                Feature.objects.get_or_create(name=feature_name)[0]
                for feature_name in features_data
            ]
            offer_detail.features.set(features)

            # Update min_price and min_delivery_time
            if min_price is None or offer_detail.price < min_price:
                min_price = offer_detail.price
            if min_delivery_time is None or offer_detail.delivery_time_in_days < min_delivery_time:
                min_delivery_time = offer_detail.delivery_time_in_days

        # Set the calculated values on the Offer instance
        offer.min_price = min_price
        offer.min_delivery_time = min_delivery_time
        offer.save()

        return offer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)

        if (request and request.method == 'POST'):
            details = []
            for detail in instance.details.all():
                # Korrigiere hier die Verarbeitung der Features
                features = []
                for feature in detail.features.all():
                    if isinstance(feature.name, str):
                        try:
                            # Entferne geschachtelte Strings, falls vorhanden
                            cleaned_name = eval(feature.name) if feature.name.startswith(
                                "{") else feature.name
                            features.append(cleaned_name)
                        except Exception:
                            features.append(feature.name)
                    else:
                        features.append(feature.name)

                details.append({
                    "id": detail.id,
                    "title": detail.title,
                    "revisions": detail.revisions,
                    "delivery_time_in_days": detail.delivery_time_in_days,
                    "price": str(detail.price),
                    "features": features,
                    "offer_type": detail.offer_type,
                })
            representation['details'] = details
        else:
            representation['details'] = self.get_details_field(instance)
        return representation

    def get_details_field(self, obj):
        """
        Retrieves a list of details associated with the given object.

        Args:
            obj: The object containing the details.

        Returns:
            A list of dictionaries, each containing the 'id' and 'url' of a detail.
        """
        return [{"id": detail.id, "url": f"/offerdetails/{detail.id}/"} for detail in obj.details.all()]

    def get_user_details_field(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }


class SingleOfferSerializer(serializers.ModelSerializer):
    """
    Serializer for a single Offer model.
    """
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

    def get_user_details_field(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        details_representation = []
        for detail in instance.details.all():
            features_representation = [
                feature.name for feature in detail.features.all()]
            details_representation.append({
                "id": detail.id,
                "title": detail.title,
                "revisions": detail.revisions,
                "delivery_time_in_days": detail.delivery_time_in_days,
                "price": str(detail.price),
                "features": features_representation,
                "offer_type": detail.offer_type,
            })

        representation['details'] = details_representation
        return representation

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        self.update_offer_fields(instance, validated_data)
        self.update_offer_details(instance, details_data)
        self.update_min_values(instance)

        return instance

    def update_min_values(self, instance):
        """
        Berechnet und aktualisiert `min_price` und `min_delivery_time` basierend
        auf den zugehörigen OfferDetails.
        """
        details = instance.details.all()

        if details.exists():
            instance.min_price = min(detail.price for detail in details)
            instance.min_delivery_time = min(
                detail.delivery_time_in_days for detail in details)
        else:
            instance.min_price = None
            instance.min_delivery_time = None

        instance.save()

    def update_offer_fields(self, instance, validated_data):
        OFFER_FIELDS = ['title', 'image', 'description', 'updated_at',
                        'min_price', 'min_delivery_time']
        for field in OFFER_FIELDS:
            setattr(instance, field, validated_data.get(
                field, getattr(instance, field)))
        instance.save()

    def update_offer_details(self, instance, details_data):
        """
        Updates or creates offer details for the given offer instance.
        Removes any existing offer details not included in the request data.
        """
        if not details_data:
            return

        existing_details = {
            detail.id: detail for detail in instance.details.all()}

        for detail_data in details_data:
            detail_id = detail_data.get('id')
            if detail_id and detail_id in existing_details:
                detail = existing_details.pop(detail_id)
                self.update_offer_detail_fields(detail, detail_data)
            else:
                self.create_offer_detail(instance, detail_data)

        for detail in existing_details.values():
            detail.delete()

    def create_offer_detail(self, instance, detail_data):
        """
        Creates a new OfferDetail instance and associates it with the given     offer.
        """
        features_data = detail_data.pop('features', [])
        new_detail = OfferDetail.objects.create(offer=instance, **detail_data)

        if features_data:
            features = self.get_or_create_features(features_data)
            new_detail.features.set(features)

        new_detail.save()

    def update_offer_detail_fields(self, offer_detail, detail_data):
        """
        Updates fields and features for an existing OfferDetail instance.
        """
        for field in ['title', 'revisions', 'delivery_time_in_days', 'price', 'offer_type']:
            setattr(offer_detail, field, detail_data.get(
                field, getattr(offer_detail, field)))

        features_data = detail_data.get('features', [])
        if features_data:
            features = self.get_or_create_features(features_data)
            offer_detail.features.set(features)

        offer_detail.save()

    def get_or_create_features(self, features_data):
        return [
            Feature.objects.get_or_create(name=feature_name)[0]
            for feature_name in features_data
        ]
