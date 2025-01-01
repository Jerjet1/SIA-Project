from django.urls import path
from . import views

urlpatterns = [
    #login url path
    path('', views.Login, name='Login'),
    path('Logout/', views.Logout, name='Logout'),
    #admin urls path
    path('Admin/Request/Status/<int:request_id>', views.approve_disapprove_request, name='admin_status_request'),
    path('Admin/Delivery/', views.create_delivery, name='create_delivery'),
    path('Admin/Delivery/Delete/<int:delivery_id>', views.delete_delivery, name='admin_delete_delivery'),
    path('Admin/Delivery/update/<int:delivery_id>', views.update_delivery, name='admin_update_delivery'),
    path('Admin/Request/', views.RequestAdmin, name='admin_request'),
    path('Admin/Inventory/', views.AdminInventory, name='admin_inventory'),
    #Admin Account url path
    path('Admin/CreateAccount/', views.AdminAccount, name='admin_create_account'),
    path('Admin/Account/', views.AccountList, name='Account_list'),
    path('Admin/Account/Status/<int:account_id>', views.account_user_status, name='admin_account_status'),
    path('Admin/Account/Update/<int:account_id>', views.UpdateAccount, name='admin_account_update'),
    path('Admin/Account/Delete/<int:account_id>', views.DeleteAccount, name='admin_account_delete'),
    #admin reports url path
    path('Admin/Reports/Job_Request', views.job_request, name='job_request_reports'),
    path('Admin/Reports/Purchase_Order_Request', views.purchase_order, name='purchase_order_reports'),
    path('Admin/Reports/Item_Request', views.item_request, name='item_request_reports'),
    path('Admin/Reports/Delivery_History', views.delivery_history, name='delivery_history_reports'),
    #supplier admin url path
    path('Admin/Supplier/Delete/<int:supplier_id>', views.delete_supplier, name='delete_supplier'),
    path('Admin/Supplier/Update/<int:supplier_id>', views.update_supplier, name='update_supplier'),
    path('Admin/Supplier/Search/', views.search_supplier, name='search_supplier'),
    path('Admin/Supplier/', views.AdminSupplier, name='admin_supplier'),
    #custodian delivery urls path
    path('Custodian/Delivery/', views.delivery_order, name='delivery_page'),
    path('Custodian/Delivery/Accept/<int:delivery_id>', views.accept_deliveries, name='accept_delivery'),
    path('Custodian/Delivery/Returned/<int:delivery_id>', views.return_deliveries, name='return_delivery'),
    #custodian inventory url path
    path('Custodian/Inventory/', views.CustodianInv, name='custodian_inventory'),
    path('Custodian/Inventory/Update/<int:inventory_id>', views.updateInventory, name='update_inventory'),
    path('Custodian/Inventory/Delete/<int:inventory_id>', views.deleteItem, name='delete_item_inventory'),
    #custodian requests url path
    path('Custodian/Request/', views.CustodianReq, name='custodian_request'),
    path('Custodian/Request/Update/<int:request_id>', views.update_request_custodian, name='custodian_update_request'),
    path('Custodian/Request/Delete/<int:request_id>', views.delete_request_custodian, name='custodian_delete_request'),
    #custodian history reports url path
    path('Custodian/Reports/Item_Request', views.Item_Reports, name='custodian_item_reports'),
    path('Custodian/Reports/Order_Request', views.order_Reports, name='custodian_order_reports'),
    #custodian delivery url path
    #worker urls path
    path('Worker/', views.WorkerReq, name='worker_home'),
    path('Worker/Request/', views.WorkerReq, name='worker_request'),
    path('Worker/Request/Update/<int:request_id>', views.update_request_worker, name='update_worker_request'),
    path('Worker/Request/Delete/<int:request_id>', views.delete_request_worker, name='delete_worker_request'),
]