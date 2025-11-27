from django.db import models
from profiles.models import UserProfile
from dishes.models import DishPortion
import uuid
from decimal import Decimal


def generate_order_number():
    return uuid.uuid4().hex[:12].upper()


class Order(models.Model):
    DELIVERY_CHOICES = (
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=32, unique=True, default=generate_order_number)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=40)
    county = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    local = models.CharField(max_length=80, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='delivery')
    pickup_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stripe_pid = models.CharField(max_length=254, null=True, blank=True)
    original_bag = models.TextField(null=True, blank=True)
    public_tracking = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.order_number

    @property
    def progress_percent(self):
        mapping = {
            'pending': 25,
            'preparing': 50,
            'out for delivery': 75,
            'completed': 100,
        }
        return mapping.get(self.status.lower(), 0)


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, related_name='lineitems', on_delete=models.CASCADE)
    portion = models.ForeignKey(DishPortion, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('order', 'portion')

    @property
    def lineitem_total(self):
        return (self.price or self.portion.price) * self.quantity
