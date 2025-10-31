import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Listing(models.Model):
    """Property/Listing model representing properties available for booking"""
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    host_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings'
    )
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    location = models.CharField(max_length=200, null=False, blank=False)
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=False,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['listing_id']),
            models.Index(fields=['host_id']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.location}"


class Booking(models.Model):
    """Booking model representing reservations made by guests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]
    
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    property_id = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=False,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=False, blank=False, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['booking_id']),
            models.Index(fields=['property_id']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.property_id.name}"


class Review(models.Model):
    """Review model for property ratings and comments"""
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    property_id = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    rating = models.IntegerField(
        null=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['review_id']),
            models.Index(fields=['property_id']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Review by {self.user_id.username} for {self.property_id.name} - {self.rating}/5"
    

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    booking = models.OneToOneField(
        'Booking', on_delete=models.CASCADE, related_name='payment'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    chapa_tx_ref = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['booking']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"