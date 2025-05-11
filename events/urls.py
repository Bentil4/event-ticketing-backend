from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register('events', EventViewSet)
router.register('categories', TicketCategoryViewSet)
router.register('promos', PromoCodeViewSet)
router.register('orders', OrderViewSet)
router.register('cart', CartItemViewSet)
router.register('tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', initiate_payment),
    path('paystack-webhook/', paystack_webhook),
]
