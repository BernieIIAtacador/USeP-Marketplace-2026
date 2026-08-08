from django.shortcuts import render

# Create your views here.
def setup_login_view(request):
    return render(request, 'accounts/login.html')