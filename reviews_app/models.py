from django.db import models
from django.contrib.auth.models import User

from user_auth_app.models import UserProfile
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Model representing a review.

    Attributes:
        business_user (ForeignKey): The business user being reviewed.
        reviewer (ForeignKey): The user who is writing the review.
        rating (PositiveIntegerField): The rating given by the reviewer.
        description (TextField): The text description of the review.
        created_at (DateTimeField): The date and time when the review was created.
        updated_at (DateTimeField): The date and time when the review was last updated.
    """
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_for_business')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_by_user')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
