from django.urls import path
from . import views

urlpatterns = [
    path('', views.Login, name='Login'),
    path('Request/', views.RequestAdmin, name='Request'),
    path('Inventory/', views.Inventory, name='Inventory'),
    path('Account/', views.Account, name='Account'),
    path('Reports/', views.Reports, name='Reports'),
    path('Supplier/', views.Supplier, name='Supplier'),
]