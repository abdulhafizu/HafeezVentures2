# Generated by Django 4.2.7 on 2023-11-19 05:39

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import operations.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0013_remove_accountpayable_customer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_serial', models.PositiveIntegerField()),
                ('material_type', models.CharField(max_length=255, validators=[operations.models.validate_no_numbers])),
                ('material_quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('is_processed', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Electricity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_ID', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('shift', models.IntegerField(choices=[(1, 'Morning'), (2, 'Night')])),
                ('meter_reading', models.DecimalField(decimal_places=2, max_digits=10)),
                ('electricity_consumption', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('electricity_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('standard_electricity_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('electricity_variance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_electricity_variance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fixed_cost_per_unit', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Expense categories',
            },
        ),
        migrations.CreateModel(
            name='GeneralExpensesAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(default='General Expenses', max_length=255)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='InitialMeterReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_reading', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Packer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('transaction_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.generalexpensesaccount')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SalaryPacker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10)),
                ('packer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.packer')),
            ],
        ),
        migrations.CreateModel(
            name='SalaryOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10)),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.operator')),
            ],
        ),
        migrations.CreateModel(
            name='SalaryManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.manager')),
            ],
        ),
        migrations.CreateModel(
            name='RecyclingOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('material_used', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bangori', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('amount1', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('customer_serial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.customerin')),
                ('meter_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.electricity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.customer')),
            ],
        ),
        migrations.CreateModel(
            name='PackerSalaryPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('packer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.packer')),
            ],
        ),
        migrations.CreateModel(
            name='OperatorSalaryPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.operator')),
            ],
        ),
        migrations.CreateModel(
            name='ManagerSalaryPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount1', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.manager')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.expensecategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'expenses',
            },
        ),
        migrations.CreateModel(
            name='AccountPayable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operations.customer')),
            ],
        ),
    ]
