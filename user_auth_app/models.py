from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Model representing a user profile.

    Attributes:
        user (OneToOneField): The user associated with this profile.
        file (ImageField): The profile image.
        location (CharField): The location of the user.
        tel (CharField): The telephone number of the user.
        description (TextField): A description of the user.
        working_hours (CharField): The working hours of the user.
        type (CharField): The type of user (customer or business).
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='profile_images', blank=True, null=True)
    location = models.CharField(
        max_length=100, blank=True, null=True, default='Unknown')
    tel = models.CharField(max_length=100, blank=True,
                           null=True, default='Unknown')
    description = models.TextField(blank=True, null=True, default='Unknown')
    working_hours = models.CharField(
        max_length=100, blank=True, null=True, default='Unknown')
    type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default='customer')

    def __str__(self):
        return f'(Id: {self.id}) - {self.user.username}'
