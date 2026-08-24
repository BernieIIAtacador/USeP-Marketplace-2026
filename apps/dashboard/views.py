from django.shortcuts import render

# Create your views here.
def setup_seller_dashboard(request):
    return render(request, 'seller/seller-dashboard.html')