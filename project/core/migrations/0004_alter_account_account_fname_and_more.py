# Generated by Django 5.1.4 on 2024-12-30 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_account_account_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_fname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_lname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_user',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='admin',
            name='admin_fname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='admin',
            name='admin_lname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='custodian_fname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='custodian_lname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_item',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_supplier',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='supplier_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='worker',
            name='worker_fname',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='worker',
            name='worker_lname',
            field=models.CharField(max_length=100),
        ),
    ]