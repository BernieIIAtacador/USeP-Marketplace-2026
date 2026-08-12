from django.shortcuts import render



# Create your views here.
def setup_login_view(request):
    return render(request, 'accounts/login.html')



def setup_verify_view(request):
    return render(request, 'verification/verify.html')

def setup_change_password_view(request):
    return render(request, 'password/change-password.html')