from django.db import models
from django.contrib.auth.models import User


class Feature(models.Model):
    """
    Model representing a feature.
    Attributes:
        name (str): The name of the feature. It must be unique and can have a maximum length of 50 characters.
    Methods:
        __str__(): Returns the string representation of the feature, which is its name.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    """
    Model representing an offer.
    Attributes:
        user (ForeignKey): A foreign key to the User model, representing the user who created the offer.
        title (CharField): The title of the offer.
        image (ImageField): An optional image associated with the offer, defaults to 'default.jpg' if not provided.
        description (TextField): A detailed description of the offer.
        created_at (DateTimeField): The date and time when the offer was created, automatically set on creation.
        updated_at (DateTimeField): The date and time when the offer was last updated, automatically set on update.
        details (ManyToManyField): A many-to-many relationship with the OfferDetail model, representing the details of the offer.
        min_price (DecimalField): The minimum price of the offer.
        min_delivery_time (PositiveIntegerField): The minimum delivery time for the offer in days.
    Methods:
        __str__(): Returns the title of the offer.
        user_details(): A property that returns a dictionary with the user's first name, last name, and username.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='images', null=True, blank=True, default='default.jpg')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    min_delivery_time = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """
    Represents the details of an offer.
    Attributes:
        title (str): The title of the offer.
        revisions (int): The number of revisions allowed for the offer.
        delivery_time_in_days (int): The delivery time in days for the offer.
        price (Decimal): The price of the offer.
        features (ManyToManyField): The features included in the offer, chosen from predefined options.
        offer_type (str): The type of the offer, chosen from predefined options.
    """

    OFFER_TYPES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    title = models.CharField(max_length=100)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.ManyToManyField(Feature)
    offer_type = models.CharField(
        max_length=20, choices=OFFER_TYPES, default="basic")
    offer = models.ForeignKey(
        Offer, related_name='details', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Order(models.Model):

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_orders')
    title = models.CharField(max_length=100)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.ManyToManyField(Feature)
    offer_type = models.CharField(
        max_length=20, choices=OfferDetail.OFFER_TYPES, default="basic")
    status = models.CharField(max_length=20, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
