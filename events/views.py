from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, TicketCategory, Order, CartItem, Ticket, PromoCode
from .serializers import *
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Order, CartItem
import hashlib
import hmac
from django.views.decorators.csrf import csrf_exempt
from .utils.email import send_ticket_email


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketCategoryViewSet(viewsets.ModelViewSet):
    queryset = TicketCategory.objects.all()
    serializer_class = TicketCategorySerializer

class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        order = self.get_object()
        order.paid = True
        order.save()
        for item in order.items.all():
            for _ in range(item.quantity):
                Ticket.objects.create(
                    order=order,
                    category=item.category,
                    original_name=f"{order.first_name} {order.surname}",
                    original_email=order.email,
                    owner_name=f"{order.first_name} {order.surname}",
                    owner_email=order.email,
                )
        return Response({'status': 'payment success and tickets created'})

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    lookup_field = 'ticket_id'

    @action(detail=True, methods=['post'])
    # def transfer(self, request, pk=None):
    #     ticket = self.get_object()
    #     ticket.owner_name = request.data.get('new_name')
    #     ticket.owner_email = request.data.get('new_email')
    #     ticket.is_transferred = True
    #     ticket.save()
    #     return Response({'status': 'ticket transferred'})

    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        if order_id:
            return Ticket.objects.filter(order_id=order_id)
        return Ticket.objects.all()


    def transfer(self, request, ticket_id=None): 
        ticket = self.get_object()
        new_name = request.data.get('new_name')
        new_email = request.data.get('new_email')

        if not new_name or not new_email:
            return Response({'error': 'Missing name or email'}, status=400)

        ticket.owner_name = new_name
        ticket.owner_email = new_email
        ticket.is_transferred = True
        ticket.save()

        return Response({'status': 'ticket transferred'})

    @action(detail=True, methods=['post'])
    def validate(self, request, ticket_id=None): 
        ticket = self.get_object()
        if ticket.is_validated:
            return Response({'status': 'already validated'}, status=400)
        ticket.is_validated = True
        ticket.save()
        return Response({'status': 'ticket validated'})



@api_view(['POST'])
def initiate_payment(request):
    order_id = request.data.get('order_id')
    order = Order.objects.get(id=order_id)

    cart_items = CartItem.objects.filter(order=order)
    total = sum(item.quantity * item.category.price for item in cart_items)

    payload = {
        "email": order.email,
        "amount": int(total * 100),
        "channels": ["mobile_money"],
        "currency": "GHS",
        "callback_url": f"http://localhost:4200/payment-success?order_id={order.id}"

    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    r = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers)

    print("Status Code:", r.status_code)
    print("Text:", r.text)

    try:
        res = r.json()
    except Exception as e:
        return Response({"error": "Invalid response from Paystack", "details": r.text}, status=500)

    if res['status']:
        order.paystack_ref = res['data']['reference']
        order.save()
        return Response({
            "authorization_url": res['data']['authorization_url'],
            "reference": res['data']['reference']
        })
    else:
        return Response({"error": res['message']}, status=400)



# Webhook endpoint 

@api_view(['POST'])
@csrf_exempt
def paystack_webhook(request):
    secret = settings.PAYSTACK_SECRET_KEY.encode()
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    body = request.body

    # Verifying the webhook signature
    computed_sig = hmac.new(secret, msg=body, digestmod=hashlib.sha512).hexdigest()
    if signature != computed_sig:
        return Response({'error': 'Invalid signature'}, status=403)

    data = json.loads(body)
    if data.get('event') == 'charge.success':
        ref = data['data']['reference']
    try:
        order = Order.objects.get(paystack_ref=ref, paid=False)
        order.paid = True
        order.save()

        for item in order.items.all():
            for _ in range(item.quantity):
                ticket = Ticket.objects.create(
                    order=order,
                    category=item.category,
                    original_name=f"{order.first_name} {order.surname}",
                    original_email=order.email,
                    owner_name=f"{order.first_name} {order.surname}",
                    owner_email=order.email
                )
                send_ticket_email(ticket) 
    except Order.DoesNotExist:
        pass

    return Response({'status': 'ok'})