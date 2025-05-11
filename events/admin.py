from django.contrib import admin
from .models import Event, TicketCategory, Order, CartItem, Ticket, PromoCode

from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Sum
from .models import Ticket, Order
from django.db import models

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage']

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'first_name', 'surname', 'email', 'paid', 'created_at']
#     list_filter = ['paid', 'created_at']
#     search_fields = ['email', 'first_name', 'surname']

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['category', 'quantity']
    can_delete = False

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ['ticket_id', 'category', 'owner_name', 'owner_email', 'is_transferred', 'is_validated']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'contact', 'paid', 'ticket_count', 'created_at']
    list_filter = ['paid', 'created_at']
    search_fields = ['first_name', 'surname', 'email']
    inlines = [CartItemInline, TicketInline]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"

    def ticket_count(self, obj):
        return obj.tickets.count()

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'category', 'quantity']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'owner_name', 'category', 'is_transferred', 'is_validated']
    list_filter = ['is_transferred', 'is_validated']
    search_fields = ['ticket_id', 'owner_email', 'owner_name']


# Analytics Dashboard

class EventAdminSite(admin.AdminSite):
    site_header = 'Event Ticketing Admin'

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('dashboard/', self.admin_view(self.dashboard_view)),
        ] + urls

    def dashboard_view(self, request):
        ticket_stats = Ticket.objects.aggregate(
            total=Count('id'),
            validated=Count('id', filter=models.Q(is_validated=True)),
            transferred=Count('id', filter=models.Q(is_transferred=True)),
        )
        order_stats = Order.objects.aggregate(
            total_orders=Count('id'),
            total_paid=Count('id', filter=models.Q(paid=True))
        )
        revenue = Ticket.objects.aggregate(
            revenue=Sum('category__price')
        )['revenue'] or 0

        return TemplateResponse(request, 'admin/dashboard.html', {
            'ticket_stats': ticket_stats,
            'order_stats': order_stats,
            'revenue': revenue,
            'title': 'Dashboard',
        })

# Use the custom admin site
event_admin = EventAdminSite(name='eventadmin')

event_admin.register(Event)
event_admin.register(TicketCategory)
event_admin.register(PromoCode)
event_admin.register(Order)
event_admin.register(Ticket)
event_admin.register(CartItem)