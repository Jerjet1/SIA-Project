#from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
#from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_list_or_404
from core.models import Request, Admin, Custodian, Worker, Item, Supplier, Account, Inventory
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def Login(request):
    return render(request, 'core/login.html')

def RequestAdmin(request):
    # requests = Request.objects.all()
    # # print(requests)
    # if not requests:
    #     messages.warning(request, 'no data available')
    # return render(request, 'core/Admin/Dashboard.html', {'requests': requests})
    return render(request, 'core/Admin/Dashboard.html')

# def fetch_requests(request):
#     # Fetch all requests data
#     requests_data = list(Requests.objects.values())
#     return JsonResponse({'requests': requests_data})


# def RequestAdmin(request):
#     return render(request, 'core/Admin/Dashboard.html',)

def AdminInventory(request):
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
        account_username = request.POST.get("username", "").strip()
        account_password = request.POST.get("password", "").strip()
        account_role = request.POST.get("role", "")

        if not (account_fname and account_lname and account_contactno and account_username and account_password and account_role):
            #message here..
            return redirect('admin_create_account')
        
        # Check if account already exists
        if Account.objects.filter(account_fname=account_fname, account_lname=account_lname, 
                                  account_user=account_username).exists():
            #messages.error(request, "An account with the same details already exists.")
            print('user already exist')
            return redirect('admin_create_account')
        else:
            account_create = Account.objects.create(
                account_fname = account_fname,
                account_lname = account_lname,
                account_contactno = account_contactno,
                account_user = account_username,
                account_pass = account_password,
                account_role = account_role
            )

            if account_role == "Admin":
                Admin.objects.create(
                    admin_fname = account_fname,
                    admin_lname = account_lname,
                    account = account_create
                )
            if account_role == "Custodian":
                Custodian.objects.create(
                    custodian_fname = account_fname,
                    custodian_lname = account_lname,
                    account = account_create
                )
            if account_role == "Workers":
                Worker.objects.create(
                    worker_fname = account_fname,
                    worker_lname = account_lname,
                    account = account_create
                )
            #message here..
            return redirect('admin_create_account')
    return render(request, 'core/Admin/Account.html')

#delete account
def DeleteAccount(request, account_id):
    pass

#update Account
def UpdateAccount(request, account_id):

    account = get_object_or_404(Account, account_id = account_id)
    if request.method == "POST":
        account_first_name = request.POST.get("first-name", "").strip().title()
        account_last_name = request.POST.get("last-name", "").strip().title()
        account_contact_no = request.POST.get("contact", "")
        account_password = request.POST.get("password", "")
        
        #validation field
        if not(account_first_name and account_last_name and account_contact_no and account_password):
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
            admin.save()
        elif account.account_role == 'Workers':
            worker = get_object_or_404(Worker, account = account_id)
            worker.worker_fname = account_first_name
            worker.worker_lname= account_last_name
            worker.save()
        elif account.account_role == 'Custodian':
            custodian = get_object_or_404(Custodian, account = account_id)
            custodian.custodian_fname = account_first_name
            custodian.custodian_lname= account_last_name
            custodian.save()

        account.account_fname = account_first_name
        account.account_lname = account_last_name
        account.account_contactno = account_contact_no
        account.account_pass = account_password
        account.save()
        #message
        return redirect('Account_list')
    return HttpResponse("invalid request method", status=405)

#display account list
def AccountList(request):
    accounts = Account.objects.all()
    return render(request, 'core/Admin/AccountList.html', {"accounts": accounts})

def AdminReports(request):
    return render(request, 'core/Admin/Reports.html')

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
    
    return HttpResponse("invalid request method", status = 405)

#delete supplier 
def delete_supplier(request, supplier_id):
    
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, supplier_id = supplier_id)
        supplier.delete()
        #messge here
        return redirect('admin_supplier')
    return HttpResponse("invalid request method", status = 405)

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
            ).filter(Q(supplier_name__icontains=search_query) |Q(item__item_name__icontains=search_query))

        else:
            suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
                'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
            )  # show all suppliers if no search term is provided

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

def deleteItem(request, inventory_id):
    if request.method == "POST":
        inventory_item = get_object_or_404(Inventory, inventory_id = inventory_id)
        delete_item = inventory_item.item
        inventory_item.delete()
        delete_item.delete()
        return redirect("custodian_inventory")
    return HttpResponse("invalid request method", status = 405)

#update inventory
def updateInventory(request, inventory_id):
    inventory_items = get_object_or_404(Inventory, inventory_id = inventory_id)
    if request.method == "POST":
        inventory_name = request.POST.get("name", "").strip().capitalize()
        inventory_descripton = request.POST.get("description", "").strip().capitalize()
        inventory_stocks = request.POST.get("stocks", "")

        #Validation input for empty value
        if not (inventory_name and inventory_descripton and inventory_stocks):
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
    return HttpResponse('invalid request method', status=405)

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

def CustodianReq(request):
    items = Item.objects.all()
    return render(request, 'core/Custodian/Request.html', {'items': items})

def CustodianReports(request):
    return render(request, 'core/Custodian/Reports.html')

def WorkerReq(request):
    items = Item.objects.all()
    return render(request, 'core/Workers/Request.html', {'items': items})