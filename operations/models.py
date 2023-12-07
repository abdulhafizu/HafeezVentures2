from _decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Expense categories"


class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Expense: {self.amount} ({self.created_at})"

    class Meta:
        verbose_name_plural = "expenses"


class GeneralExpensesAccount(models.Model):
    account_name = models.CharField(max_length=255, default="General Expenses")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def credit(self, amount, description=""):
        self.balance += amount
        self.description = description
        self.save()

    def debit(self, amount, description=""):
        if self.balance >= amount:
            self.balance -= amount
            self.description = description  # Set the description for the debit
            self.save()
        else:
            raise ValueError("Insufficient balance")

    def __str__(self):
        return self.account_name


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    account = models.ForeignKey(GeneralExpensesAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.account.account_name}"

    class Meta:
        ordering = ['-created_at']


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    # Add any other fields specific to your Customer model.

    def __str__(self):
        return self.name


class Packer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    # Add any other fields specific to your Customer model.

    def __str__(self):
        return self.name


class Operator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    # Add any other fields specific to your Customer model.

    def __str__(self):
        return self.name


class Manager(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ElectricityConfiguration(models.Model):
    fixed_cost_per_unit = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Electricity Configuration - N{self.fixed_cost_per_unit} per unit"


class InitialMeterReading(models.Model):
    initial_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Initial Meter Reading: {self.initial_reading}"


def validate_no_numbers(value):
    if any(char.isdigit() for char in value):
        raise ValidationError("Numbers are not allowed in this field.")


class CustomerIn(models.Model):
    customer_serial = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=255, validators=[validate_no_numbers])
    material_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.customer_serial)


class Electricity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meter_ID = models.CharField(max_length=100)
    date = models.DateField()
    shift = models.IntegerField(choices=((1, 'Morning'), (2, 'Night')))
    meter_reading = models.DecimalField(max_digits=10, decimal_places=2)

    electricity_consumption = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electricity_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_meter_reading = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def get_rate_from_recycling_operation(self):
        # Define your logic here to get the rate from RecyclingOperation
        # This method should return the rate
        pass

    def __str__(self):
        return str(self.meter_ID)


class RecyclingOperation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    meter_ID = models.ForeignKey(Electricity, on_delete=models.CASCADE)
    customer_serial = models.ForeignKey(CustomerIn, on_delete=models.CASCADE)
    material_used = models.DecimalField(max_digits=10, decimal_places=2)
    bangori = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    standard_electricity_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electricity_variance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    packer = models.ForeignKey(Packer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Recycling Operation - CustomerIn: {str(self.customer_serial)}, Date: {self.meter_ID.date}"


class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    due_date = models.DateTimeField(auto_now_add=True)


class AccountPayable(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateTimeField(auto_now_add=True)


class SalaryManager(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))

    def __str__(self):
        return "Salary Manager"

    def nil_accounts(self):
        self.manager = 0
        self.save()


class SalaryOperator(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))

    def __str__(self):
        return "Salary Operator"

    def nil_accounts(self):
        self.operator = 0
        self.save()


class SalaryPacker(models.Model):
    packer = models.ForeignKey(Packer, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))

    def __str__(self):
        return "Salary Packer"

    def nil_accounts(self):
        self.packer = 0
        self.save()


class ManagerSalaryPayment(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    due_date = models.DateTimeField(auto_now_add=True)


class OperatorSalaryPayment(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    due_date = models.DateTimeField(auto_now_add=True)


class PackerSalaryPayment(models.Model):
    packer = models.ForeignKey(Packer, on_delete=models.CASCADE)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    due_date = models.DateTimeField(auto_now_add=True)


class FlakesIn(models.Model):
    serial = models.CharField(max_length=100)
    date = models.DateField()
    flakes_type = models.CharField(max_length=255, validators=[validate_no_numbers])
    flakes_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.serial)


class FlakesCost(models.Model):
    cost_id = models.CharField(max_length=100)
    cost_of_washing = models.DecimalField(max_digits=10, decimal_places=2)
    cost_of_transport = models.DecimalField(max_digits=10, decimal_places=2)
    pelleting_cost = models.DecimalField(max_digits=10, decimal_places=2)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.cost_id)


class PelletsPrice(models.Model):
    date = models.DateField()
    serial = models.ForeignKey(FlakesIn, on_delete=models.CASCADE)
    cost_id = models.ForeignKey(FlakesCost, on_delete=models.CASCADE)
    pellets_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return 'Pellet Price'