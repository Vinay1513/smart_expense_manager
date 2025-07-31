from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Category(models.Model):
    """Category model for expenses and transactions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    icon = models.CharField(max_length=50, default='receipt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Transaction model for parsed PDF transactions"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Original transaction ID from PDF")
    date = models.DateField()
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='debit')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='success')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='UPI')
    source_file = models.CharField(max_length=255, blank=True, help_text="Original PDF filename")
    raw_data = models.JSONField(default=dict, help_text="Original parsed row data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.transaction_type})"

    @property
    def is_credit(self):
        return self.transaction_type == 'credit'

    @property
    def is_debit(self):
        return self.transaction_type == 'debit'


class Expense(models.Model):
    """Expense model for manual expense tracking"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('phonepe', 'PhonePe'),
        ('paytm', 'Paytm'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='expense')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class PhonePeTransaction(models.Model):
    """PhonePe specific transaction model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phonepe_transactions')
    transaction_date = models.DateField()
    merchant_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=50, default='PhonePe')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"{self.merchant_name} - {self.amount}" 