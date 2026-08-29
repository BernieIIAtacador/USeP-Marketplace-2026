from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('seller/', views.setup_seller_dashboard, name='seller'),
    path('buyer/', views.setup_buyer_dashboard, name='buyer'),
    path('buyer/cart/', views.setup_buyer_cart, name='buyer_cart'),
    path('buyer/<slug:item_slug>/', views.setup_buyer_item_detail, name='buyer_detail'),
]