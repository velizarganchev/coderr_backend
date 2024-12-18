from django.db import models
from django.contrib.auth.models import User

from offers_app.models import Feature, OfferDetail
from django.core.validators import MinValueValidator


class Order(models.Model):
    """
    Order model represents a customer's order in the system.
    Attributes:
        ORDER_STATUSES (list): List of possible statuses for an order.
        customer_user (ForeignKey): Reference to the user who is the customer.
        business_user (ForeignKey): Reference to the user who is the business owner.
        title (CharField): Title of the order.
        revisions (PositiveIntegerField): Number of revisions allowed for the order.
        delivery_time_in_days (PositiveIntegerField): Delivery time for the order in days.
        price (DecimalField): Price of the order.
        features (ManyToManyField): Features included in the order.
        offer_type (CharField): Type of offer associated with the order.
        status (CharField): Current status of the order.
        created_at (DateTimeField): Timestamp when the order was created.
        updated_at (DateTimeField): Timestamp when the order was last updated.
    Methods:
        __str__(): Returns the string representation of the order, which is its title.
    """

    ORDER_STATUSES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_orders')
    title = models.CharField(max_length=100)
    revisions = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-1)],
        help_text="Number of revisions allowed. Use -1 for unlimited revisions."
    )
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.ManyToManyField(Feature)
    offer_type = models.CharField(
        max_length=20, choices=OfferDetail.OFFER_TYPES, default="basic")
    status = models.CharField(
        max_length=20, choices=ORDER_STATUSES, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
