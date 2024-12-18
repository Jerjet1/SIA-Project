from django.urls import path
from . import views

urlpatterns = [
    path('', views.Login, name='Login'),
    path('Admin/Request/', views.RequestAdmin, name='Admin/Request'),
    path('Admin/Inventory/', views.Inventory, name='Admin/Inventory'),
    path('Admin/Account/', views.Account, name='Admin/Account'),
    path('Admin/Reports/', views.Reports, name='Admin/Reports'),
    path('Admin/Supplier/', views.Supplier, name='Admin/Supplier'),
    path('Custodian/Inventory/', views.CustodianInv, name='Custodian/Inventory'),
    path('Custodian/Request/', views.CustodianReq, name='Custodian/Request'),
    path('Custodian/Reports/', views.CustodianReports, name='Custodian/Reports'),
    path('Worker/Request/', views.WorkerReq, name='Worker/Request'),
]