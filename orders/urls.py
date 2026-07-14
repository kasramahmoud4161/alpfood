from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CartView, AddToCartView, RemoveFromCartView, 
    UpdateCartItemView, CheckoutView, OrderViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/update/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', include(router.urls)),
]