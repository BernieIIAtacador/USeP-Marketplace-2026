from django.urls import path
from . import views

urlpatterns=[
    path('', views.dashboard_view, name='dashboard'),
    path('seller/', views.seller_view, name='seller'),
    path('seller/add/', views.add_listing_view, name='add_listing'),
    path('seller/items/<int:item_id>/', views.manage_item_view, name='manage_item'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.setup_change_password_view, name='change_password'),
    path('login/', views.setup_login_view, name='login'),
    path('verify/', views.setup_verify_view, name='verify')
]