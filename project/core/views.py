from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from core.models import Request, Admin, Custodian, Worker, Item, Supplier, Account, Inventory, Delivery,Reports
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def Admin_user(request,user_id):
    try:
        admin_user = Account.objects.get(account_id = user_id)
        if admin_user.account_role == 'Admin':
            return True
        elif admin_user.account_role == 'Workers':
            return redirect('worker_home')
        elif admin_user.account_role == 'Custodian':
            return redirect('custodian_request')
    except Account.DoesNotExist:
        return redirect('Login')
    
def Custodian_user(request, user_id):
    try:
        custodian_user = Account.objects.get(account_id = user_id)
        if custodian_user.account_role == 'Custodian':
            return True
        elif custodian_user.account_role == 'Workers':
            return redirect('worker_home')
        else:
            return redirect('admin_request')
    except Account.DoesNotExist:
        return redirect('Login')
    
def Worker_user(request, user_id):
    try:
        worker_user = Account.objects.get(account_id = user_id)
        if worker_user.account_role == 'Workers':
            return True
        elif worker_user.account_role == 'Custodian':
            return redirect('custodian_request')
        else:
            return redirect('admin_request')
    except Account.DoesNotExist:
        return redirect('Login')
    
# function for pagination
def pagination_history(request ,requests_history):

    paginator = Paginator(requests_history, 10)
    page = request.GET.get('page', 1)
    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)
    
    return paginated

# Create your views here.
def Logout(request):
    request.session.flush()
    return redirect('Login')

def Login(request):
    
    if request.session.get('account_id'):
        user_id = request.session.get('account_id')
        try:
            user = Account.objects.get(account_id=user_id)
            # Redirect user based on their role if they are already logged in
            if user.account_role == 'Workers': 
                return redirect('worker_home')
            elif user.account_role == 'Custodian':
                return redirect('custodian_request')
            else:
                return redirect('admin_request')
        except Account.DoesNotExist:
            messages.error(request, 'Account does not exist')
            return redirect('Login')

    if request.method == 'POST':
        username = request.POST.get('user').strip()
        password = request.POST.get('password').strip()
        try:
            user = Account.objects.get(account_user = username)
            if user.account_pass == password:
                if user.account_status == 'active':
                    request.session['account_id'] = user.account_id
                    request.session['account_role'] = user.account_role
                    if user.account_role == 'Workers':
                        return redirect('worker_home')
                    elif user.account_role == 'Custodian':
                        return redirect('custodian_request')
                    else:
                        return redirect('admin_request')
                else:
                    messages.error(request,'Account has been deactivate contact your admin')
                    return redirect('Login')
            else:
                print('Invalid password')
                messages.error(request, 'invalid password')
                return redirect('Login')
        except Account.DoesNotExist:
            messages.error(request, 'Account does not exist')
            return redirect('Login')
    return render(request, 'core/login.html')

#approve/disapprove for admin
def approve_disapprove_request(request, request_id):
    if request.method == 'POST':
        try:
            requested_form = Request.objects.get(request_id = request_id)
            status = request.POST.get("status")
            approve_status = "Approve"
            decline_status = "Decline"
            if status == 'approve':
                if requested_form.request_type == 'Item Request':
                    items = Inventory.objects.get(item = requested_form.item)
                    if items.inventory_quantity < requested_form.request_item_quantity:
                        messages.error(request,'insufficient stocks')
                        return redirect('admin_request')
                    else:
                        quantity = items.inventory_quantity - requested_form.request_item_quantity
                        items.inventory_quantity = quantity
                        items.save()
                        requested_form.request_status = approve_status
                        requested_form.save()
                        Reports.objects.create(
                            request = requested_form
                        )
                        return redirect('admin_request')
                else:
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
        except Http404:
            messages.error(request, 'the request has been deleted or not exist.')
            return redirect('admin_request')
        except Exception:
            messages.error(request, "unexpected error occured")
            return redirect('admin_request')
    return redirect('admin_request')

#Request page Admin
def RequestAdmin(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        requests = Request.objects.all().filter(request_status = 'Pending').order_by('-request_date')
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'requests': requests,
            'admin_name': admin_name,
        }
        return render(request, 'core/Admin/Dashboard.html', display_data)
    return result

#add items in inventory
def AdminInventory(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:

        #select_related joins in database query
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        items = Inventory.objects.select_related('item').values(
            'inventory_id',
            'item__item_name',
            'item__item_description',
            'inventory_quantity',
        ).order_by('inventory_quantity')
        display_data = {
            'admin_name': admin_name,
            'items': items,
        }

        if request.method == "POST":
            item_name = request.POST.get("name", "").strip().capitalize()
            item_description = request.POST.get("description", "").strip().capitalize()

            if not (item_name and item_description):
                return redirect("admin_inventory")
            
            if Item.objects.filter(item_name=item_name).exists():
                messages.error(request, 'item already exist')
                return redirect('admin_inventory')
            try:
                item = Item.objects.create(
                    item_name = item_name,
                    item_description = item_description
                )

                Inventory.objects.create(
                    item = item
                )
                messages.success(request, 'added successfully')
                return redirect("admin_inventory")
            except ValidationError as e:
                messages.error(request, 'Validation error occured'+ str(e))
                return redirect('admin_inventory')
        return render(request, 'core/Admin/Inventory.html', display_data)
    return result

#create Account
def AdminAccount(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
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
            check_user = len(Account.objects.filter(account_fname=account_fname, account_lname=account_lname))
            check_username = len(Account.objects.filter(account_user = account_username))
            # Check if account already exists
            if check_username:
                messages.error(request, "Username already exist.")
                return redirect('admin_create_account')
            if check_user:
                messages.error(request, "User already exist.")
                return redirect('admin_create_account')
            else:
                try:
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
                except IntegrityError as e:
                    messages.error(request, 'database error'+ str(e))
                except ValidationError as e: #maximum lenghth of field or trying to insert a string in int/decimal field datatype
                    messages.error(request, 'Validation error'+ str(e))
                except Exception as e:
                    messages.error(request, 'unexpected error occured'+ str(e))
        return render(request, 'core/Admin/Account.html', {'admin_name': admin_name})
    return result

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
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        accounts = Account.objects.all().order_by('account_role', 'account_status')
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'accounts': accounts,
            'admin_name': admin_name,
        }
        return render(request, 'core/Admin/AccountList.html', display_data)
    return result

#report for job request
def job_request(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        
        status_filter = request.GET.get('status-job', 'all')

        if status_filter == 'Approve':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_quantity', 'request', 'request__request_date',
                'request__request_item_name', 'request__request_user', 'request__request_status', 'request__request_repair_details',
            ).filter(request__request_type = 'Job Request', request__request_status = 'Approve').order_by('-report_date', '-report_id')
            print("Status Filter:", status_filter)
        elif status_filter == 'Decline':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_quantity', 'request', 'request__request_date',
                'request__request_item_name', 'request__request_user', 'request__request_status', 'request__request_repair_details',
            ).filter(request__request_type = 'Job Request', request__request_status = 'Decline').order_by('-report_date', '-report_id')
            print("Status Filter:", status_filter)
        else:
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_quantity', 'request', 'request__request_date',
                'request__request_item_name', 'request__request_user', 'request__request_status', 'request__request_repair_details',
            ).filter(request__request_type = 'Job Request').order_by('-report_date', '-report_id')

        paginated = pagination_history(request, requests)
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'requests': paginated,
            'admin_name': admin_name,
            'status_filter': status_filter,
        }
        return render(request, 'core/Admin/JobRequest.html', display_data)
    return result

#report for purchase order
def purchase_order(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        status_filter = request.GET.get('status-order', 'all')
        if status_filter == 'Approve':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order', request__request_status = 'Approve').order_by('-report_date','-report_id')
        elif status_filter == 'Decline':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order', request__request_status = 'Decline').order_by('-report_date','-report_id')
        else:
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order').order_by('-report_date','-report_id')


        paginated = pagination_history(request, requests)
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'status_filter': status_filter,
            'requests': paginated,
            'admin_name': admin_name,
        }
        return render(request, 'core/Admin/OrderRequest.html', display_data)
    return result

#report for item_request
def item_request(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        status_filter = request.GET.get('status-item', 'all')
        if status_filter == 'Approve':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request', request__request_status = 'Approve').order_by('-report_date', '-report_id')
        elif status_filter == 'Decline':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request', request__request_status = 'Decline').order_by('-report_date', '-report_id')
        else:
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request').order_by('-report_date', '-report_id')
        
        paginated = pagination_history(request, requests)
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'status_filter': status_filter,
            'requests': paginated,
            'admin_name': admin_name,
        }
        return render(request, 'core/Admin/RequestReport.html', display_data)
    return result

#report for deliver history
def delivery_history(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        status_filter = request.GET.get('status', 'all')

        if status_filter == 'Returned':
            reports = Reports.objects.all().select_related('delivery', 'delivery__supplier').values(
                'report_id', 'report_date', 'report_reason', 'delivery__delivery_item', 'delivery__delivery_quantity', 'delivery__delivery_supplier',
                'delivery__delivery_total', 'delivery__delivery_status', 'delivery__delivery_id', 'delivery__supplier__supplier_price', 
            ).filter(delivery__delivery_status = 'Returned').order_by('-report_date', '-report_id')
        elif status_filter == 'Delivered':
            reports = Reports.objects.all().select_related('delivery', 'delivery__supplier').values(
                'report_id', 'report_date', 'report_reason', 'delivery__delivery_item', 'delivery__delivery_quantity', 'delivery__delivery_supplier',
                'delivery__delivery_total', 'delivery__delivery_status', 'delivery__delivery_id', 'delivery__supplier__supplier_price', 
            ).filter(delivery__delivery_status = 'Delivered').order_by('-report_date', '-report_id')
        else:
            reports = Reports.objects.all().select_related('delivery', 'delivery__supplier').values(
                'report_id', 'report_date', 'report_reason', 'delivery__delivery_item', 'delivery__delivery_quantity', 'delivery__delivery_supplier',
                'delivery__delivery_total', 'delivery__delivery_status', 'delivery__delivery_id', 'delivery__supplier__supplier_price', 
            ).filter(delivery__delivery_status__in = ['Delivered', 'Returned']).order_by('-report_date', '-report_id')

        paginated_reports = pagination_history(request, reports)
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'status_filter': status_filter,
            # 'reports': reports,
            'admin_name': admin_name,
            'reports': paginated_reports,
        }
        return render(request, 'core/Admin/DeliveryReport.html', display_data)
    return result

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
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        # Fetch items and suppliers for display
        items = Item.objects.all()
        #select_related joins in database query
        suppliers = Supplier.objects.select_related('item').values('supplier_id','supplier_name','supplier_address',
            'supplier_contactno','item__item_name','supplier_price','supplier_grade','item_id',
        ).order_by('supplier_price')
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        display_data = {
            'suppliers': suppliers,
            'items': items,
            'admin_name': admin_name,
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
                messages.error(request, 'supplier already exist')
                return redirect('admin_supplier')
            try:
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
                messages.success(request, 'supplier create successfully')
                return redirect('admin_supplier')
            except Http404:
                messages.error(request, 'item not found')
                return redirect('admin_supplier')
            except ValidationError as e:
                messages.error(request, 'Validation error'+ str(e))
                return redirect('admin_supplier')
        return render(request, 'core/Admin/Supplier.html', display_data)
    return result

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
                messages.error(request, 'unexpected error')
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
            messages.success(request, 'Update successfully')
            return redirect('create_delivery')
        except Http404:
            #message here..
            messages.error(request, 'object not found 404')
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
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Admin_user(request, user)
    if result == True:
        items = Item.objects.all()
        suppliers = Supplier.objects.all()
        pending_delivery = Delivery.objects.all().filter(delivery_status = 'Pending')
        admin_user = Account.objects.get(account_id = user)
        admin_name = admin_user.account_fname
        grouped_suppliers = {}
        for item in items:
            grouped_suppliers[item.item_id] = suppliers.filter(item = item)
        
        display_data = {
            'items': items,
            'grouped_suppliers': grouped_suppliers,
            'pending_delivery': pending_delivery,
            'admin_name': admin_name,
        }

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
            try:
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
            except Http404:
                messages.error(request, 'object not found')
                return redirect('create_delivery')
            except ValidationError as e:
                messages.error(request, 'Validation error')
                return redirect('Create_delivery')
        return render(request, 'core/Admin/Delivery.html', display_data)
    return result

def deleteItem(request, inventory_id):
    if request.method == "POST":
        inventory_item = get_object_or_404(Inventory, inventory_id = inventory_id)
        if inventory_item and inventory_item.inventory_quantity !=0:
            messages.error(request, 'cannot delete still have stocks')
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
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Custodian_user(request, user)
    if result == True:
        #select_related joins in database query
        items = Inventory.objects.select_related('item').values('inventory_id','item__item_name',
            'item__item_description','inventory_quantity','item').order_by('inventory_quantity')
        custodian_user = Account.objects.get(account_id = user)
        custodian_name = custodian_user.account_fname
        display_data = {
            'items': items,
            'custodian_name': custodian_name
        }

        if request.method == "POST":
            item_name = request.POST.get("name", "").strip().capitalize()
            item_description = request.POST.get("description", "").strip().capitalize()

            if not (item_name and item_description):
                return redirect("custodian_inventory")
            
            if Item.objects.filter(item_name=item_name).exists():
                messages.error(request, 'item already exist')
                return redirect('custodian_inventory')

            item = Item.objects.create(
                item_name = item_name,
                item_description = item_description
            )

            Inventory.objects.create(
                item = item
            )
            messages.success(request, 'added successfully')
        return render(request, 'core/Custodian/Inventory.html', display_data)
    return result

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
            messages.success(request, 'update successfully')
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
            messages.success(request, 'update successfully')
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
        except Exception:
            messages.error(request, 'unexpected error occured')
            return redirect('custodian_request')
    return redirect('custodian_request')

#custodian request job and purchase order
def CustodianReq(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Custodian_user(request, user)
    if result == True:
        items = Item.objects.all()
        custodian_session = get_object_or_404(Custodian, account = user)
        request_custodian = Request.objects.filter(request_type__in = ["Job Request", "Purchase Order"], 
                                                   request_status = 'Pending', custodian = custodian_session)
        custodian_user = Account.objects.get(account_id = user)
        custodian_name = custodian_user.account_fname
        custodian_user_name = custodian_user.account_fname + ' ' + custodian_user.account_lname

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
                try:
                    request_item = get_object_or_404(Item, item_id = custodian_requst_item)
                    Request.objects.create(
                        request_type = custodian_request_type,
                        request_user = custodian_user_name,
                        request_item_name = request_item.item_name,
                        request_item_quantity = custodian_request_quantity,
                        item = request_item,
                        custodian = custodian_session
                    )
                    #message
                    return redirect('custodian_request')
                except Http404:
                    messages.error(request, 'object not found')
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
                    request_user = custodian_user_name,
                    custodian = custodian_session
                )
                return redirect('custodian_request')
            
        display_data = {
            'items': items,
            'request_custodian': request_custodian,
            'custodian_name': custodian_name,
        }                
        return render(request, 'core/Custodian/Request.html', display_data)
    return result

# accept/return order
def accept_deliveries(request, delivery_id):
    
    if request.method == 'POST':
        try:
            quantity = request.POST.get('quantity', '')
            total = request.POST.get('total', '')
            updated_total = float(total)
            updated_quantity = int(quantity)
            status = 'Delivered'
            delivery = get_object_or_404(Delivery, delivery_id = delivery_id)
            inventory = Inventory.objects.get(item = delivery.item)         
            total_quantity = inventory.inventory_quantity + updated_quantity
            
            inventory.inventory_quantity = total_quantity
            inventory.save()

            delivery.delivery_quantity = quantity
            delivery.delivery_total = updated_total
            delivery.delivery_status = status
            delivery.save()
            Reports.objects.create(
                delivery = delivery
            )
            messages.success(request, 'transaction complete')
            return redirect('delivery_page')
        except Exception:
            messages.error(request, 'unexpected error occured')
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
            messages.success(request, 'transaction complete')
            return redirect('delivery_page')
        except Exception:
            messages.error(request, 'unexpected error occured')
            return redirect('delivery_page')
    return redirect('delivery_page')

#display deliveries
def delivery_order(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Custodian_user(request, user)
    if result == True:
        check_deliveries = Delivery.objects.all().filter(delivery_status = 'Pending').select_related('supplier')
        custodian_user = Account.objects.get(account_id = user)
        custodian_name = custodian_user.account_fname
        display_data = {
            'check_deliveries': check_deliveries,
            'custodian_name': custodian_name,
        }
        return render(request, 'core/Custodian/Delivery.html', display_data)
    return result

#custodian reports
def order_Reports(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Custodian_user(request, user)
    if result == True:
        status_filter = request.GET.get('status-order', 'all')

        if status_filter == 'Approve':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order', request__request_status = 'Approve').order_by('-report_date')
        elif status_filter == 'Decline':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order', request__request_status = 'Decline').order_by('-report_date')
        else:
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type',
                'request__request_item_quantity', 'request__request_item_name', 'request__request_date',
                'request__request_status', 'request__item', 'request', 'request__request_user'
            ).filter(request__request_type = 'Purchase Order').order_by('-report_date')

        paginated = pagination_history(request, requests)
        custodian_user = Account.objects.get(account_id = user)
        custodian_name = custodian_user.account_fname
        display_data = {
            'status_filter' : status_filter,
            'requests': paginated,
            'custodian_name': custodian_name,
        }
        return render(request, 'core/Custodian/OrderRequest.html', display_data)
    return result

def Item_Reports(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Custodian_user(request, user)
    if result == True:
        status_filter = request.GET.get('status-item', 'all')
        if status_filter == 'Approve':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request', request__request_status = 'Approve').order_by('-report_date')
        elif status_filter == 'Decline':
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request', request__request_status = 'Decline').order_by('-report_date')
        else:
            requests = Reports.objects.all().select_related('request').values(
                'report_id', 'report_date', 'request__request_type', 'request__request_item_name',
                'request__request_item_quantity', 'request__request_date', 'request__request_status', 'request', 'request__request_user'
            ).filter(request__request_type = 'Item Request').order_by('-report_date')

        paginated = pagination_history(request, requests)
        custodian_user = Account.objects.get(account_id = user)
        custodian_name = custodian_user.account_fname
        display_data = {
            'status_filter': status_filter,
            'requests': paginated,
            'custodian_name': custodian_name,
        }
        return render(request, 'core/Custodian/RequestReports.html', display_data)
    return result

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
        messages.success(request, 'update successfully')
        return redirect('worker_request')
    return redirect('worker_request')
    
# Worker create request(partial)
def WorkerReq(request):
    user = request.session.get('account_id')
    if not user:
        return redirect('Login')
    result = Worker_user(request, user)
    if result == True:
        try:
            workers_id = get_object_or_404(Worker, account = user)
        except Worker.DoesNotExist:
            messages.error(request, 'Unexpected occured')
            return redirect('Login')
        worker_request_type = Request.objects.all().filter(request_type ="Item Request",
                                                            request_status = 'Pending', worker = workers_id)
        inventory_item = Inventory.objects.select_related('item').values(
            'item__item_id',
            'inventory_quantity',
            'item__item_name',
        )
        worker_display_name = workers_id.worker_fname
        worker_user = workers_id.worker_fname + ' '+ workers_id.worker_lname
        display_data = {
            'inventory_item': inventory_item,
            'worker_request_type': worker_request_type,
            'worker_display_name': worker_display_name,
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
                messages.error(request, 'insufficient stocks')
                return redirect('worker_request')
            
            try:
                item = get_object_or_404(Item, item_id = item_request)
            except:
                return redirect('worker_request')

            Request.objects.create(
                request_type = item_request_type,
                request_item_name = item.item_name,
                request_item_quantity = item_request_quantity,
                request_user = worker_user,
                item = item,
                worker = workers_id
            )
            return redirect('worker_request')
        return render(request, 'core/Workers/Request.html', display_data)
    return result