import uuid
from django.db import models
# from typing import TYPE_CHECKING
# Create your models here.
# from django.db import models

# """Model representing event details"""
class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)

# ''' Model representing Ticket Category'''
class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.PositiveIntegerField(default=0)

# ''' Model representing order'''
class Order(models.Model):
    paystack_ref = models.CharField(max_length=100, blank=True, null=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

# ''' Model representing add to cart'''
class CartItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# ''' Model representing Tickets'''
# class Ticket(models.Model):
#     ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     order = models.ForeignKey(Order, related_name='tickets', on_delete=models.CASCADE)
#     category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
#     owner_name = models.CharField(max_length=200)
#     owner_email = models.EmailField()
#     is_transferred = models.BooleanField(default=False)
#     is_validated = models.BooleanField(default=False)

class Ticket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, related_name='tickets', on_delete=models.CASCADE)
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    
    # Original buyer info (never overwritten)
    original_name = models.CharField(max_length=200)
    original_email = models.EmailField()

    # Current owner info (may change on transfer)
    owner_name = models.CharField(max_length=200)
    owner_email = models.EmailField()

    is_transferred = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.ticket_id)

