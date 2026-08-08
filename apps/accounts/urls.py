from django.urls import path
from . import views

urlpatterns=[
    path('login/', views.setup_login_view, name='login')
]