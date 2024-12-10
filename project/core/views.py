from django.shortcuts import render

# Create your views here.
def Dashboard(request):
    return render(request, 'core/Admin/Dashboard.html')

def Inventory(request):
    return render(request, 'core/Admin/Inventory.html')

def Account(request):
    return render(request, 'core/Admin/Account.html')

def Reports(request):
    return render(request, 'core/Admin/Reports.html')

def Supplier(request):
    return render(request, 'core/Admin/Supplier.html')