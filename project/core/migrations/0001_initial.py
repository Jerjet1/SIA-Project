# Generated by Django 5.1.4 on 2024-12-24 10:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('account_fname', models.CharField(max_length=25)),
                ('account_lname', models.CharField(max_length=25)),
                ('account_contactno', models.CharField(max_length=25)),
                ('account_address', models.CharField(max_length=25)),
                ('account_user', models.CharField(max_length=25)),
                ('account_pass', models.CharField(max_length=25)),
                ('account_role', models.CharField(choices=[('Workers', 'Workers'), ('Admin', 'Admin'), ('Custodian', 'Custodian')], max_length=25)),
                ('account_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=25)),
            ],
            options={
                'db_table': 'account',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=25)),
                ('item_description', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'item',
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('admin_id', models.AutoField(primary_key=True, serialize=False)),
                ('admin_fname', models.CharField(max_length=25)),
                ('admin_lname', models.CharField(max_length=25)),
                ('admin_contactno', models.CharField(max_length=15)),
                ('admin_address', models.CharField(max_length=50)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.account')),
            ],
            options={
                'db_table': 'admin',
            },
        ),
        migrations.CreateModel(
            name='Custodian',
            fields=[
                ('custodian_id', models.AutoField(primary_key=True, serialize=False)),
                ('custodian_fname', models.CharField(max_length=25)),
                ('custodian_lname', models.CharField(max_length=25)),
                ('custodian_contactno', models.CharField(max_length=15)),
                ('custodian_address', models.CharField(max_length=50)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.account')),
            ],
            options={
                'db_table': 'custodian',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('inventory_id', models.AutoField(primary_key=True, serialize=False)),
                ('inventory_quantity', models.SmallIntegerField(default=0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.item')),
            ],
            options={
                'db_table': 'inventory',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('delivery_id', models.AutoField(primary_key=True, serialize=False)),
                ('delivery_item', models.CharField(max_length=50)),
                ('delivery_quantity', models.CharField(max_length=25)),
                ('delivery_supplier', models.CharField(max_length=25)),
                ('delivery_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_date', models.DateField(auto_now_add=True)),
                ('delivery_status', models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Returned', 'Returned')], default='Pending', max_length=25)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.item')),
            ],
            options={
                'db_table': 'delivery',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('request_id', models.AutoField(primary_key=True, serialize=False)),
                ('request_type', models.CharField(choices=[('Job Request', 'Job Request'), ('Item Request', 'Item Request'), ('Purchase Order', 'Purchase Order')], max_length=25)),
                ('request_user', models.CharField(max_length=50)),
                ('request_item_quantity', models.SmallIntegerField(blank=True, null=True)),
                ('request_repair_details', models.CharField(blank=True, max_length=255, null=True)),
                ('request_item_name', models.CharField(blank=True, max_length=50, null=True)),
                ('request_date', models.DateField(auto_now_add=True)),
                ('request_status', models.CharField(choices=[('Pending', 'Pending'), ('Approve', 'Approve'), ('Decline', 'Decline')], default='Pending', max_length=25)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.admin')),
                ('custodian', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.custodian')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.item')),
            ],
            options={
                'db_table': 'request',
            },
        ),
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('report_id', models.AutoField(primary_key=True, serialize=False)),
                ('report_date', models.DateField(auto_now_add=True)),
                ('report_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('delivery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.delivery')),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.request')),
            ],
            options={
                'db_table': 'reports',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False)),
                ('supplier_name', models.CharField(max_length=50)),
                ('supplier_address', models.CharField(max_length=100)),
                ('supplier_contactno', models.CharField(max_length=25)),
                ('supplier_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('supplier_grade', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('B', 'C')], max_length=10)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.item')),
            ],
            options={
                'db_table': 'supplier',
            },
        ),
        migrations.AddField(
            model_name='delivery',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.supplier'),
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('worker_id', models.AutoField(primary_key=True, serialize=False)),
                ('worker_fname', models.CharField(max_length=25)),
                ('worker_lname', models.CharField(max_length=25)),
                ('worker_contactno', models.CharField(max_length=15)),
                ('worker_address', models.CharField(max_length=50)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.account')),
            ],
            options={
                'db_table': 'worker',
            },
        ),
        migrations.AddField(
            model_name='request',
            name='worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.worker'),
        ),
    ]
