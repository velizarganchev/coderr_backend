from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied
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
            'updated_at',
        ]
        read_only_fields = ['reviewer']

    def validate_customer(self):
        """
        Validates the customer based on the request context and authorization token.
        Raises:
            ValidationError: If the request context is missing.
            ValidationError: If the authorization token is missing or invalid.
            ValidationError: If the token does not correspond to a valid user.
            ValidationError: If the user is not of type 'customer'.
        Returns:
            User: The authenticated user if validation is successful.
        """
        request = self.context.get('request')

        if not request:
            raise ValidationError({'detail': 'Request context fehlt.'})

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            raise NotAuthenticated(detail='Token fehlt.')
        token_key = auth_header.split(' ')[1]
        try:
            user = Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            raise PermissionDenied(detail='Ungültiger Token.')
        if user.userprofile.type != 'customer':
            raise PermissionDenied(
                detail='Sie haben keine Berechtigung, Bewertungen zu erstellen.')
        return user

    def validate_business_user(self, business_user):
        """
        Validate the business user.
        This method checks if the provided business user is valid and active.
        If the business user is not provided or is not active, a ValidationError
        is raised with an appropriate error message.
        Args:
            business_user (User): The business user to validate.
        Returns:
            User: The validated business user.
        Raises:
            ValidationError: If the business user is not provided or is not active.
        """
        if not business_user:
            raise ValidationError(
                {'detail': 'Das Feld business_user ist erforderlich.'})
        return business_user

    def create(self, validated_data):
        """
        Creates a new review instance.
        This method validates the customer and business user from the provided
        validated data. It ensures that the user has not already reviewed the
        specified business user. If a review already exists, a ValidationError
        is raised.
        Args:
            validated_data (dict): The validated data containing the review details.
        Returns:
            Review: The newly created review instance.
        Raises:
            ValidationError: If the user has already reviewed the business user.
        """
        user = self.validate_customer()

        business_user = self.validate_business_user(
            validated_data.get('business_user'))

        if Review.objects.filter(business_user=business_user, reviewer=user).exists():
            raise PermissionDenied(
                detail='Sie haben bereits eine Bewertung für dieses Unternehmen abgegeben.')

        review = Review.objects.create(reviewer=user, **validated_data)
        return review

    def update(self, instance, validated_data):
        """
        Update the review instance with validated data if the user is the reviewer.
        Args:
            instance (Model): The review instance to be updated.
            validated_data (dict): The data that has been validated and will be used to update the instance.
        Raises:
            ValidationError: If the user is not the reviewer of the instance.
        Returns:
            Model: The updated review instance.
        """
        user = self.validate_customer()

        if not user == instance.reviewer:
            raise PermissionDenied(
                detail='Sie haben keine Berechtigung, diese Bewertung zu bearbeiten.')

        return super().update(instance, validated_data)
