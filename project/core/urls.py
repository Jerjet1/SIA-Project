from django.urls import path
from . import views

urlpatterns = [
    #login url path
    path('', views.Login, name='Login'),
    #admin urls path
    path('Admin/Request/', views.RequestAdmin, name='admin_request'),
    path('Admin/', views.RequestAdmin, name='admin_home'),
    path('Admin/Inventory/', views.AdminInventory, name='admin_inventory'),
    #Admin Account url path
    path('Admin/CreateAccount/', views.AdminAccount, name='admin_create_account'),
    path('Admin/Account/', views.AccountList, name='Account_list'),
    path('Admin/Account/Update/<int:account_id>', views.UpdateAccount, name='admin_account_update'),
    path('Admin/Account/Delete/<int:account_id>', views.DeleteAccount, name='admin_account_delete'),
    #admin reports url path
    path('Admin/Reports/', views.AdminReports, name='admin_reports'),
    #supplier admin url path
    path('Admin/Supplier/Delete/<int:supplier_id>', views.delete_supplier, name='delete_supplier'),
    path('Admin/Supplier/Update/<int:supplier_id>', views.update_supplier, name='update_supplier'),
    path('Admin/Supplier/Search/', views.search_supplier, name='search_supplier'),
    path('Admin/Supplier/', views.AdminSupplier, name='admin_supplier'),
    #custodian urls path
    path('Custodian/', views.CustodianReq, name='custodian_home'),
    #custodian inventory url path
    path('Custodian/Inventory/', views.CustodianInv, name='custodian_inventory'),
    path('Custodian/Inventory/Update/<int:inventory_id>', views.updateInventory, name='update_inventory'),
    path('Custodian/Inventory/Delete/<int:inventory_id>', views.deleteItem, name='delete_item_inventory'),
    #custodian requests url path
    path('Custodian/Request/', views.CustodianReq, name='custodian_request'),
    #custodian history reports url path
    path('Custodian/Reports/', views.CustodianReports, name='custodian_reports'),
    #worker urls path
    path('Worker/', views.WorkerReq, name='worker_home'),
    path('Worker/Request/', views.WorkerReq, name='worker_request'),
]

# urlpatterns = [
#     # path('fetchData/', views.fetch_requests, name='fetchData'),
#     path('', views.Login, name='Login'),
#     path('Admin/Request/', views.RequestAdmin, name='Admin/Request'),
#     path('Admin/', views.RequestAdmin, name='Admin/'),
#     path('Admin/Inventory/', views.AdminInventory, name='Admin/Inventory'),
#     path('Admin/CreateAccount/', views.AdminAccount, name='Admin/CreateAccount'),
#     path('Admin/Account/', views.AccountList, name='Admin/Account'),
#     path('Admin/Reports/', views.AdminReports, name='Admin/Reports'),
#     path('Admin/Supplier/', views.AdminSupplier, name='Admin/Supplier'),
#     path('Custodian/', views.CustodianReq, name='Custodian/'),
#     path('Custodian/Inventory/', views.CustodianInv, name='Custodian/Inventory'),
#     path('Custodian/Request/', views.CustodianReq, name='Custodian/Request'),
#     path('Custodian/Reports/', views.CustodianReports, name='Custodian/Reports'),
#     path('Worker/', views.WorkerReq, name='Worker/'),
#     path('Worker/Request/', views.WorkerReq, name='Worker/Request'),
# ]