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

def AccountList(request):
    return render(request, 'core/Admin/AccountList.html')

def Reports(request):
    return render(request, 'core/Admin/Reports.html')

def Supplier(request):
    return render(request, 'core/Admin/Supplier.html')

def CustodianInv(request):
    return render(request, 'core/Custodian/Inventory.html')

def CustodianReq(request):
    return render(request, 'core/Custodian/Request.html')

def CustodianReports(request):
    return render(request, 'core/Custodian/Reports.html')

def WorkerReq(request):
    return render(request, 'core/Workers/Request.html')