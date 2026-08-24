from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('seller/', views.setup_seller_dashboard, name='seller'),
]