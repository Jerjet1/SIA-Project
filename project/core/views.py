#from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
#from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_list_or_404
from core.models import Request, Admin, Custodian, Worker, Item, Supplier, Account, Inventory, Delivery,Reports
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def Login(request):
    

    return render(request, 'core/login.html')

def approve_disapprove_request(request, request_id):

    try:
        requested_form = get_object_or_404(Request, request_id = request_id)
    except:
        return redirect('admin_request')
    
    approve_status = "Approve"
    decline_status = "Decline"
    if request.method == 'POST':
        status = request.POST.get("status")
        if status == 'approve':
            requested_form.request_status = approve_status
            requested_form.save()
            Reports.objects.create(
                request = requested_form
            )
            return redirect('admin_request')
        if status == 'decline':
            requested_form.request_status = decline_status
            requested_form.save()
            Reports.objects.create(
                request = requested_form
            )
            return redirect('admin_request')
    return redirect('admin_request')

def RequestAdmin(request):
    requests = Request.objects.all().filter(request_status = 'Pending').order_by('request_date')
    if not requests:
        messages.warning(request, 'no data available')
    return render(request, 'core/Admin/Dashboard.html', {'requests': requests})

#add items in inventory
def AdminInventory(request):

    if request.method == "POST":
        item_name = request.POST.get("name", "").strip().capitalize()
        item_description = request.POST.get("description", "").strip().capitalize()

        if not (item_name and item_description):
            return redirect("admin_inventory")
        
        if Item.objects.filter(item_name=item_name).exists():
            #message here
            return redirect('admin_inventory')

        item = Item.objects.create(
            item_name = item_name,
            item_description = item_description
        )

        Inventory.objects.create(
            item = item
        )
        return redirect("admin_inventory")
    #select_related joins in database query
    items = Inventory.objects.select_related('item').values(
        'inventory_id',
        'item__item_name',
        'item__item_description',
        'inventory_quantity',
    )
    return render(request, 'core/Admin/Inventory.html', {'items': items})

#create Account
def AdminAccount(request):

    if request.method == "POST":
        account_fname = request.POST.get("fname").strip().capitalize()
        account_lname = request.POST.get("lname").strip().capitalize()
        account_contactno = request.POST.get("contactno", "")
        account_address = request.POST.get("address","").strip().capitalize()
        account_username = request.POST.get("username", "").strip()
        account_password = request.POST.get("password", "").strip()
        account_role = request.POST.get("role", "")

        if not (account_fname and account_lname and account_contactno 
                and account_username and account_password and account_role and account_address):
            #message here..
            return redirect('admin_create_account')
        
        # Check if account already exists
        if Account.objects.filter(account_fname=account_fname, account_lname=account_lname, 
                                  account_user=account_username).exists():
            messages.error(request, "An account with the same details already exists.")
            print('user already exist')
            return redirect('admin_create_account')
        else:
            account_create = Account.objects.create(
                account_fname = account_fname,
                account_lname = account_lname,
                account_contactno = account_contactno,
                account_address = account_address,
                account_user = account_username,
                account_pass = account_password,
                account_role = account_role
            )

            if account_role == "Admin":
                Admin.objects.create(
                    admin_fname = account_fname,
                    admin_lname = account_lname,
                    admin_contactno = account_contactno,
                    admin_address = account_address,
                    account = account_create
                )
            if account_role == "Custodian":
                Custodian.objects.create(
                    custodian_fname = account_fname,
                    custodian_lname = account_lname,
                    custodian_contactno = account_contactno,
                    custodian_address = account_address,
                    account = account_create
                )
            if account_role == "Workers":
                Worker.objects.create(
                    worker_fname = account_fname,
                    worker_lname = account_lname,
                    worker_contactno = account_contactno,
                    worker_address = account_address,
                    account = account_create
                )
            messages.success(request, "Account successfully created.")
            return redirect('admin_create_account')
    return render(request, 'core/Admin/Account.html')

#delete account
def DeleteAccount(request, account_id):
    user_account = get_object_or_404(Account, account_id = account_id)
    if request.method == 'POST':
        user_account.delete()
        return redirect('Account_list')
    return redirect('Account_list')

#update Account
def UpdateAccount(request, account_id):

    account = get_object_or_404(Account, account_id = account_id)
    if request.method == "POST":
        account_first_name = request.POST.get("first-name", "").strip().title()
        account_last_name = request.POST.get("last-name", "").strip().title()
        account_contact_no = request.POST.get("contact", "")
        account_add = request.POST.get("address","").strip().title()
        account_password = request.POST.get("password", "")
        
        #validation field
        if not(account_first_name and account_last_name and account_contact_no and account_password and account_add):
            #message here
            return redirect('Account_list')
        
        if Account.objects.filter(account_fname=account_first_name, account_lname=account_last_name).exclude(
            account_id=account_id).exists():
            #message here
            print('not updated')
            return redirect('Account_list')
        
        if account.account_role == 'Admin':
            admin = get_object_or_404(Admin, account = account_id)
            admin.admin_fname = account_first_name
            admin.admin_lname = account_last_name
            admin.admin_contactno = account_contact_no
            admin.admin_address = account_add
            admin.save()
        elif account.account_role == 'Workers':
            worker = get_object_or_404(Worker, account = account_id)
            worker.worker_fname = account_first_name
            worker.worker_lname= account_last_name
            worker.worker_contactno = account_contact_no
            worker.worker_address = account_add
            worker.save()
        elif account.account_role == 'Custodian':
            custodian = get_object_or_404(Custodian, account = account_id)
            custodian.custodian_fname = account_first_name
            custodian.custodian_lname= account_last_name
            custodian.custodian_contactno = account_contact_no
            custodian.custodian_address = account_add
            custodian.save()

        account.account_fname = account_first_name
        account.account_lname = account_last_name
        account.account_contactno = account_contact_no
        account.account_address = account_add
        account.account_pass = account_password
        account.save()
        #message
        return redirect('Account_list')
    return redirect('Account_list')

# Activate/deactivate account
def account_user_status(request, account_id):
    user_account = get_object_or_404(Account, account_id = account_id)
    if request.method == 'POST':
        if user_account.account_status == 'active':
            user_account.account_status = 'inactive'
            user_account.save()
            return redirect('Account_list')
        else:
            user_account.account_status = 'active'
            user_account.save()
            return redirect('Account_list')
    return redirect('Account_list')

#display account list
def AccountList(request):
    accounts = Account.objects.all()
    return render(request, 'core/Admin/AccountList.html', {"accounts": accounts})

#report for job request
def job_request(request):
    requests = Reports.objects.all().select_related('request').values(
        'report_id', 'report_date', 'request__request_type', 'request__request_item_quantity', 'request', 'request__request_date',
        'request__request_item_name', 'request__request_user', 'request__request_status', 'request__request_repair_details',
    ).filter(request__request_type = 'Job Request')
    return render(request, 'core/Admin/JobRequest.html', {'requests': requests})

#report for purchase order
def purchase_order(request):
    requests = Reports.objects.all().select_related('request').values(
        'report_id', 'report_date', 'request__request_type',
        'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
        'request__request_status', 'request__item', 'request', 'request__request_user'
    ).filter(request__request_type = 'Purchase Order')
    return render(request, 'core/Admin/OrderRequest.html', {'requests': requests})

#report for item_request
def item_request(request):
    requests = Reports.objects.all().select_related('request').values(
        'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
        'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
    ).filter(request__request_type = 'Item Request')
    return render(request, 'core/Admin/RequestReport.html', {'requests': requests})

#report for deliver history
def delivery_history(request):
    reports = Reports.objects.all().select_related('delivery', 'delivery__supplier').values(
        'report_id', 'report_date', 'report_reason', 'delivery__delivery_item', 'delivery__delivery_quantity', 'delivery__delivery_supplier',
        'delivery__delivery_total', 'delivery__delivery_status', 'delivery__delivery_id', 'delivery__supplier__supplier_price', 
    ).filter(delivery__delivery_status__in = ['Delivered', 'Returned']).order_by('-report_date')
    return render(request, 'core/Admin/DeliveryReport.html', {'reports': reports})

#update supplier
def update_supplier(request, supplier_id):

    suppliers = get_object_or_404(Supplier, supplier_id = supplier_id)
    if request.method == 'POST':
        supplier_name = request.POST.get("name", "").strip().title()
        supplier_address = request.POST.get("address", "").strip().title()
        supplier_contactno = request.POST.get("contactno", "")
        supplier_price = request.POST.get("price", "")
        supplier_grade = request.POST.get("grade", "")
        item_id = request.POST.get("items")

        # Validate input fields
        if not all([suppliers.supplier_name and suppliers.supplier_address and suppliers.supplier_contactno and 
                 suppliers.supplier_price and suppliers.supplier_grade and item_id]):
            # Return an error message (can also pass this to the template)
            return redirect('admin_supplier')
        
        item = get_object_or_404(Item, item_id = item_id)

        # Update supplier object
        suppliers.supplier_name = supplier_name
        suppliers.supplier_address = supplier_address
        suppliers.supplier_contactno = supplier_contactno
        suppliers.supplier_price = supplier_price
        suppliers.supplier_grade = supplier_grade
        suppliers.item = item

        suppliers.save()
        return redirect('admin_supplier')
    return redirect('admin_supplier')

#delete supplier 
def delete_supplier(request, supplier_id):
    
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, supplier_id = supplier_id)
        supplier.delete()
        #messge here
        return redirect('admin_supplier')
    return redirect('admin_supplier')

# search for supplier // pwede rani wagtangon bullshit
def search_supplier(request):
    #select_related joins in database query
    suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
        'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
    )

    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        
        if search_query:
            suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
                'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
            ).filter(Q(supplier_name__icontains=search_query) |Q(item__item_name__icontains=search_query)
                     |Q(supplier_grade__icontains = search_query)|Q(supplier_price__icontains = search_query))

        else:
            suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
                'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
            )  # show all suppliers if no search term is provided
            return redirect('admin_supplier')

    return render(request, 'core/Admin/Supplier.html', {"suppliers": suppliers})

#add supplier also a landing page in supplier
def AdminSupplier(request):
    # Fetch items and suppliers for display
    items = Item.objects.all()
    #select_related joins in database query
    suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
        'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
    ).order_by('supplier_price')

    display_data = {
        'suppliers': suppliers,
        'items': items,
    }

    if request.method == 'POST':
        # Retrieve and sanitize inputs
        supplier_name = request.POST.get("name", "").strip().title()
        supplier_address = request.POST.get("address", "").strip().title()
        supplier_contactno = request.POST.get("contact_no", "")
        supplier_price = request.POST.get("price", "")
        supplier_grade = request.POST.get("grade", "")
        item_id = request.POST.get("items")

        # Validate input fields
        if not (supplier_name and supplier_address and supplier_contactno and supplier_price and supplier_grade and item_id):
            # Return an error message (can also pass this to the template)
            return redirect('admin_supplier')

        # Check if the supplier name already exists
        if Supplier.objects.filter(supplier_name=supplier_name).exists():
            return redirect('admin_supplier')

        # Fetch the associated item
        item = get_object_or_404(Item, item_id=item_id)

        # Create and save the new supplier
        Supplier.objects.create(
            supplier_name=supplier_name,
            supplier_address=supplier_address,
            supplier_contactno=supplier_contactno,
            supplier_price=supplier_price,
            supplier_grade=supplier_grade,
            item=item
        )
        #message here
        return redirect('admin_supplier')

    return render(request, 'core/Admin/Supplier.html', display_data)

#update delivery
def update_delivery(request, delivery_id):
    if request.method == 'POST':
        try:
            update_deliver = get_object_or_404(Delivery, delivery_id = delivery_id)
            delivery_update_item = request.POST.get('item')
            delivery_update_supplier = request.POST.get('supplier_id')
            delivery_update_quantity = request.POST.get('quantity')
            total = request.POST.get('total')

            try:
                delivery_update_total = float(total)
            except ValueError:
                # Add appropriate error message or handling
                return redirect('create_delivery')
            
            item = get_object_or_404(Item, item_id = delivery_update_item)
            supplied = get_object_or_404(Supplier, supplier_id = delivery_update_supplier)

            update_deliver.delivery_item = item.item_name
            update_deliver.delivery_supplier = supplied.supplier_name
            update_deliver.delivery_quantity = delivery_update_quantity
            update_deliver.delivery_total = delivery_update_total
            update_deliver.supplier = supplied
            update_deliver.item = item
            update_deliver.save()
            print('Update successfully')
            #message here...
            return redirect('create_delivery')
        except:
            #message here..
            print('Unexpected error')
            return redirect('create_delivery')
    return redirect('create_delivery')

def delete_delivery(request, delivery_id):
    if request.method == 'POST':
        try:
            delete_deliver = get_object_or_404(Delivery, delivery_id = delivery_id)
            delete_deliver.delete()
            return redirect('create_delivery')
        except:
            #message
            return redirect('create_delivery')
        #message here...
    return redirect('create_delivery')

def create_delivery(request):
    items = Item.objects.all()
    suppliers = Supplier.objects.all()
    pending_delivery = Delivery.objects.all().filter(delivery_status = 'Pending')

    grouped_suppliers = {}
    for item in items:
        grouped_suppliers[item.item_id] = suppliers.filter(item = item)
    
    if request.method == 'POST':
        create_delivery_item = request.POST.get('item', "")
        create_delivery_quantity = request.POST.get('quantity', "")
        create_delivery_supplier = request.POST.get('supplier_id', "")
        total = request.POST.get('total', "")

        try:
            create_delivery_total = float(total)
        except ValueError:
            # Add appropriate error message or handling
            return redirect('create_delivery')
        
        quantity = int(create_delivery_quantity)
        if not (create_delivery_item and create_delivery_quantity and create_delivery_supplier and total):
            #message here..
            return redirect('create_delivery')
        
        if quantity <= 0:
            #message here...
            return redirect('create_delivery')
        
        item = get_object_or_404(Item, item_id = create_delivery_item)
        supplied = get_object_or_404(Supplier, supplier_id = create_delivery_supplier)

        Delivery.objects.create(
            delivery_item = item.item_name,
            delivery_quantity = create_delivery_quantity,
            delivery_supplier = supplied.supplier_name,
            delivery_total = create_delivery_total,
            supplier = supplied,
            item = item,
        )
        #message...
        return redirect('create_delivery')

    display_data = {
        'items': items,
        'grouped_suppliers': grouped_suppliers,
        'pending_delivery': pending_delivery,
    }
    return render(request, 'core/Admin/Delivery.html', display_data)

def deleteItem(request, inventory_id):
    if request.method == "POST":
        inventory_item = get_object_or_404(Inventory, inventory_id = inventory_id)
        if inventory_item and inventory_item.inventory_quantity !=0:
            print("cannot delete still have stocks")
            return redirect('custodian_inventory')
        else:
            delete_item = inventory_item.item
            inventory_item.delete()
            delete_item.delete()
            return redirect("custodian_inventory")
    return redirect("custodian_inventory")

#update inventory
def updateInventory(request, inventory_id):
    inventory_items = get_object_or_404(Inventory, inventory_id = inventory_id)
    if request.method == "POST":
        inventory_name = request.POST.get("name", "").strip().capitalize()
        inventory_descripton = request.POST.get("description", "").strip().capitalize()
        stocks = request.POST.get("stocks", "")
        inventory_stocks = int(stocks)
        #Validation input for empty value
        if not (inventory_name and inventory_descripton and stocks):
            return redirect('custodian_inventory')
        
        item = inventory_items.item

        #update inventory
        item.item_name = inventory_name
        item.item_description = inventory_descripton
        inventory_items.inventory_quantity = inventory_stocks

        item.save()
        inventory_items.save()
        #message here..

        return redirect('custodian_inventory')
    return redirect('custodian_inventory')

#add items in inventory
def CustodianInv(request):
    
    if request.method == "POST":
        item_name = request.POST.get("name", "").strip().capitalize()
        item_description = request.POST.get("description", "").strip().capitalize()

        if not (item_name and item_description):
            return redirect("custodian_inventory")
        
        if Item.objects.filter(item_name=item_name).exists():
            #message here
            return redirect('custodian_inventory')

        item = Item.objects.create(
            item_name = item_name,
            item_description = item_description
        )

        Inventory.objects.create(
            item = item
        )

    #select_related joins in database query
    items = Inventory.objects.select_related('item').values('inventory_id','item__item_name',
        'item__item_description','inventory_quantity','item').order_by('inventory_quantity')

    return render(request, 'core/Custodian/Inventory.html', {'items': items})

def update_request_custodian(request, request_id):
    
    custodian_request = get_object_or_404(Request, request_id = request_id)
    if request.method == 'POST':
        custodian_request_type = request.POST.get("request-type")
        if custodian_request_type == 'Job Request':
            #job request
            custodian_request_item = request.POST.get("item").strip().capitalize()
            quantity = request.POST.get("quantity")
            custodian_request_details = request.POST.get("repair").strip()
            custodian_request_quantity = int(quantity)

            if not (custodian_request_item and custodian_request_details and quantity):
                #message here..
                return redirect('custodian_request')
            
            if custodian_request_quantity <= 0:
                #message here..
                return redirect('custodian_request')
            custodian_request.request_item_name = custodian_request_item
            custodian_request.request_item_quantity = custodian_request_quantity
            custodian_request.request_repair_details = custodian_request_details
            custodian_request.save()
            #message
            return redirect('custodian_request')
        else:
            #purchase order
            custodian_request_item = request.POST.get("items")
            quantity = request.POST.get("quantity")
            custodian_request_quantity = int(quantity)
            if not (custodian_request_item and quantity):
                #message here..
                return redirect('custodian_request')
            
            if custodian_request_quantity <= 0:
                #message here..
                return redirect('custodian_request')
            
            items = get_object_or_404(Item, item_id = custodian_request_item)
            custodian_request.request_item_name = items.item_name
            custodian_request.request_item_quantity = custodian_request_quantity
            custodian_request.item = items
            custodian_request.save()
            #message
            return redirect('custodian_request')
    return redirect('custodian_request')

# Custodian delete Request
def delete_request_custodian(request, request_id):
    
    if request.method == 'POST':
        try:
            delete_request = get_object_or_404(Request, request_id = request_id)
            delete_request.delete()
            #message here..
            return redirect('custodian_request')
        except:
            #message here..
            return redirect('custodian_request')
    return redirect('custodian_request')

#custodian request job and purchase order
def CustodianReq(request):
    items = Item.objects.all()
    request_custodian = Request.objects.filter(request_type__in = ["Job Request", "Purchase Order"], request_status = 'Pending')
    try:
        custodian_user = get_object_or_404(Custodian, custodian_id = 2)
        user_request = custodian_user.custodian_fname + " " +custodian_user.custodian_lname
    except:
        return redirect('Login')
    if request.method == "POST":
        custodian_request_type = request.POST.get("request-type")
        
        #purchase order
        if custodian_request_type == "Purchase Order":
            custodian_requst_item = request.POST.get("items")
            quantity_value = request.POST.get("quantity")

            custodian_request_quantity = int(quantity_value)
            #validation
            if not (custodian_requst_item and quantity_value.isdigit()):
                #message here..
                return redirect('custodian_request')
            if custodian_request_quantity <= 0:
                #message here..
                return redirect('custodian_request')
            
            request_item = get_object_or_404(Item, item_id = custodian_requst_item)
            Request.objects.create(
                request_type = custodian_request_type,
                request_user = user_request,
                request_item_name = request_item.item_name,
                request_item_quantity = custodian_request_quantity,
                item = request_item,
                custodian = custodian_user
            )
            #message
            return redirect('custodian_request')
        else:
            #job order field
            custodian_request_item_job = request.POST.get("item").strip().capitalize()
            custodian_request_quantity_job = int(request.POST.get("quantity"))
            custodian_request_repair_details = request.POST.get("repair").strip().capitalize()

            #validation
            if not (custodian_request_item_job and custodian_request_quantity_job and custodian_request_repair_details):
                #message here..
                return redirect('custodian_request')
            
            if custodian_request_quantity_job <= 0:
                #message here..
                return redirect('custodian_request')
            
            Request.objects.create(
                request_type = custodian_request_type,
                request_item_quantity = custodian_request_quantity_job,
                request_repair_details = custodian_request_repair_details,
                request_item_name = custodian_request_item_job,
                request_user = user_request,
                custodian = custodian_user
            )
            return redirect('custodian_request')
        
    display_data = {
        'items': items,
        'request_custodian': request_custodian
    }
            
    return render(request, 'core/Custodian/Request.html', display_data)

# accept/return order
def accept_deliveries(request, delivery_id):
    
    if request.method == 'POST':
        try:
            status = 'Delivered'
            delivery = get_object_or_404(Delivery, delivery_id = delivery_id)

            delivery.delivery_status = status
            delivery.save()
            Reports.objects.create(
                delivery = delivery
            )
            #message here..
            return redirect('delivery_page')
        except:
            print('unexpected error occured.')
            return redirect('delivery_page')
    return redirect('delivery_page')

def return_deliveries(request, delivery_id):

    if request.method == 'POST':
        try:
            returned = request.POST.get('reason', "").strip()
            status = 'Returned'
            delivery = get_object_or_404(Delivery, delivery_id = delivery_id)

            if not returned:
                #message here..
                return redirect('delivery_page')

            delivery.delivery_status = status
            delivery.save()
            Reports.objects.create(
                delivery = delivery,
                report_reason = returned
            )
            return redirect('delivery_page')
        except:
            #message here..
            return redirect('delivery_page')
    return redirect('delivery_page')

#display deliveries
def delivery_order(request):
    check_deliveries = Delivery.objects.all().filter(delivery_status = 'Pending')
    return render(request, 'core/Custodian/Delivery.html', {'check_deliveries': check_deliveries})

#custodian reports
def order_Reports(request):
    requests = Reports.objects.all().select_related('request').values(
        'report_id', 'report_date', 'request__request_type',
        'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
        'request__request_status', 'request__item', 'request', 'request__request_user'
    ).filter(request__request_type = 'Purchase Order')
    return render(request, 'core/Custodian/OrderRequest.html', {'requests': requests})

def Item_Reports(request):
    requests = Reports.objects.all().select_related('request').values(
        'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
        'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
    ).filter(request__request_type = 'Item Request')
    return render(request, 'core/Custodian/RequestReports.html', {'requests': requests})

# Worker Delete Request
def delete_request_worker(request, request_id):
    
    if request.method == 'POST':
        worker_request = get_object_or_404(Request, request_id = request_id)
        worker_request.delete()
        #messsage here..
        return redirect('worker_request')
    return redirect('worker_request')

#update request worker
def update_request_worker(request, request_id):
    user_request = get_object_or_404(Request, request_id = request_id)
    if request.method == 'POST':
        user_request_item = request.POST.get("items")
        user_request_quantity = request.POST.get("quantity")

        #validation
        if not (user_request_item and user_request_quantity):
            #message here..
            return redirect('worker_request')
        
        items = get_object_or_404(Item, item_id = user_request_item)

        user_request.request_item_quantity = user_request_quantity
        user_request.request_item_name = items.item_name
        user_request.item = items
        user_request.save()
        return redirect('worker_request')
    return redirect('worker_request')
    
# Worker create request(partial)
def WorkerReq(request):
    try:
        workers_id = get_object_or_404(Worker, worker_id = 2)
        user_request = workers_id.worker_fname + " " + workers_id.worker_lname
    except:
        return redirect('Login')
    worker_request_type = Request.objects.all().filter(request_type ="Item Request", request_status = 'Pending')
    inventory_item = Inventory.objects.select_related('item').values(
        'item__item_id',
        'inventory_quantity',
        'item__item_name',
    )
    display_data = {
        'inventory_item': inventory_item,
        'worker_request_type': worker_request_type
    }

    if request.method == "POST":
        item_request_type = request.POST.get("request-type")
        item_request = request.POST.get("items")
        quantity_item = request.POST.get("quantity")
        item_request_quantity = int(quantity_item)
        #validation
        if not (quantity_item.isdigit() and item_request_type):  
            #message here...
            return redirect('worker_request')
        try:
            inventory = get_object_or_404(Inventory, item = item_request)
        except:
            return redirect('worker_request')
        
        if item_request_quantity <= 0 or item_request_quantity > inventory.inventory_quantity:
            #message here...
            print('insufficient stocks')
            return redirect('worker_request')
        
        try:
            item = get_object_or_404(Item, item_id = item_request)
        except:
            return redirect('worker_request')

        Request.objects.create(
            request_type = item_request_type,
            request_item_name = item.item_name,
            request_item_quantity = item_request_quantity,
            request_user = user_request,
            item = item,
            worker = workers_id
        )
        return redirect('worker_request')
    return render(request, 'core/Workers/Request.html', display_data)