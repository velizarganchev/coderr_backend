from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='profile_images', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default='customer')

    def __str__(self):
        return f'(Id: {self.id}) - {self.user.username}'
