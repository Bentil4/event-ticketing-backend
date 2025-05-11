from rest_framework import serializers
from .models import Event, TicketCategory, Order, CartItem, Ticket, PromoCode

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    categories = TicketCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = '__all__'

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
