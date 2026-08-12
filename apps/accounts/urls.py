from django.urls import path
from . import views

urlpatterns=[
    path('change-password/', views.setup_change_password_view, name='change_password'),
    path('login/', views.setup_login_view, name='login'),
    path('verify/', views.setup_verify_view, name='verify')
]