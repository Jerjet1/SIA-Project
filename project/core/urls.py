from django.urls import path
from . import views

urlpatterns = [
    path(' ', views.Dashboard, name='Dashboard'),
    path('Inventory/', views.Inventory, name='Inventory'),
    path('Account/', views.Account, name='Account'),
    path('Reports/', views.Reports, name='Reports'),
    path('Supplier/', views.Supplier, name='Supplier'),
]