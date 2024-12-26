# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Account(models.Model):
    ROLE_CHOICES = [
        ('Workers', 'Workers'),
        ('Admin', 'Admin'),
        ('Custodian', 'Custodian'),
    ]

    STATUS_CHOICES = [ 
        ('active', 'Active'), 
        ('inactive', 'Inactive'), 
        ]

    account_id = models.AutoField(primary_key=True)
    account_fname = models.CharField(max_length=25)
    account_lname = models.CharField(max_length=25)
    account_contactno = models.CharField(max_length=25)
    account_address = models.CharField(max_length=25)
    account_user = models.CharField(max_length=25)
    account_pass = models.CharField(max_length=25)
    account_role = models.CharField(max_length=25, choices=ROLE_CHOICES)
    account_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'account'


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_fname = models.CharField(max_length=25)
    admin_lname = models.CharField(max_length=25)
    admin_contactno = models.CharField(max_length=15)
    admin_address = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'admin'

class Worker(models.Model):
    worker_id = models.AutoField(primary_key=True)
    worker_fname = models.CharField(max_length=25)
    worker_lname = models.CharField(max_length=25)
    worker_contactno = models.CharField(max_length=15)
    worker_address = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'worker'

class Custodian(models.Model):
    custodian_id = models.AutoField(primary_key=True)
    custodian_fname = models.CharField(max_length=25)
    custodian_lname = models.CharField(max_length=25)
    custodian_contactno = models.CharField(max_length=15)
    custodian_address = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'custodian'

class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=25)
    item_description = models.CharField(max_length=25)

    class Meta:
        db_table = 'item'


class Request(models.Model):

    REQUEST_TYPE = [
        ('Job Request', 'Job Request'),
        ('Item Request', 'Item Request'),
        ('Purchase Order', 'Purchase Order'),
    ]

    STATUS_CHOICE = [
        ('Pending', 'Pending'),
        ('Approve', 'Approve'),
        ('Decline', 'Decline'),
    ]

    request_id = models.AutoField(primary_key=True)
    request_type = models.CharField(max_length=25, choices=REQUEST_TYPE)
    request_user = models.CharField(max_length=50, blank=False, null=False)
    request_item_quantity = models.SmallIntegerField(blank=True, null=True)
    request_repair_details = models.CharField(max_length=255, blank=True, null=True)
    request_item_name = models.CharField(max_length=50, blank=True, null=True)
    request_date = models.DateField(auto_now_add=True)
    request_status = models.CharField(max_length=25, choices=STATUS_CHOICE, default='Pending')
    item = models.ForeignKey(Item, models.SET_NULL, blank=True, null=True)
    worker = models.ForeignKey(Worker, models.SET_NULL, blank=True, null=True)
    custodian = models.ForeignKey(Custodian, models.SET_NULL, blank=True, null=True)
    admin = models.ForeignKey(Admin, models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'request'

class Supplier(models.Model):

    GRADE_CHOICE = [
        ('A', 'A'),
        ('B', 'B'),
        ('B', 'C'),
    ]

    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=50)
    supplier_address = models.CharField(max_length=100)
    supplier_contactno = models.CharField(max_length=25)
    supplier_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_grade = models.CharField(max_length=10, choices=GRADE_CHOICE)
    item = models.ForeignKey(Item, models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'supplier'

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    inventory_quantity = models.SmallIntegerField(default= 0)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        db_table = 'inventory'

class Delivery(models.Model):

    status = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
    ]

    delivery_id = models.AutoField(primary_key=True)
    delivery_item = models.CharField(max_length=50)
    delivery_quantity = models.CharField(max_length=25)
    delivery_supplier = models.CharField(max_length=25)
    delivery_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_status = models.CharField(max_length=25, choices=status, default='Pending')
    supplier = models.ForeignKey(Supplier, models.SET_NULL, blank=True, null=True)
    item = models.ForeignKey(Item, models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'delivery'

class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_date = models.DateField(auto_now_add=True)
    report_reason = models.CharField(max_length=255, blank=True, null=True)
    request = models.ForeignKey(Request, models.SET_NULL, blank=True, null=True)
    delivery = models.ForeignKey(Delivery, models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'reports'
