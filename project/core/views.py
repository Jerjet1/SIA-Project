from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def Login(request):
    return render(request, 'core/login.html')

def RequestAdmin(request):
    return render(request, 'core/Admin/Dashboard.html')

def Inventory(request):
    return render(request, 'core/Admin/Inventory.html')

def Account(request):
    return render(request, 'core/Admin/Account.html')

def Reports(request):
    return render(request, 'core/Admin/Reports.html')

def Supplier(request):
    return render(request, 'core/Admin/Supplier.html')