from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Value
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models.functions import Coalesce
from django.views.generic.edit import CreateView, UpdateView
from .models import (Expense, RecyclingOperation, ElectricityConfiguration, AccountPayable, Payment,
                     GeneralExpensesAccount, Manager, Operator, Packer, SalaryManager, SalaryPacker, SalaryOperator,
                     ManagerSalaryPayment, Transaction, CustomerIn, OperatorSalaryPayment, PackerSalaryPayment,
                     InitialMeterReading, Electricity, FlakesIn, FlakesCost, PelletsPrice, )
from decimal import Decimal
from allauth.account.views import LoginView


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        general_expenses_account = GeneralExpensesAccount.objects.first()
        context['account'] = general_expenses_account
        return context


class CustomLoginView(LoginView):
    template_name = 'login.html'


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['amount', 'description', 'category']
    template_name = 'expenses/create-expense.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        expense_amount = form.cleaned_data['amount']

        general_expenses_account = GeneralExpensesAccount.objects.first()
        if general_expenses_account.balance >= expense_amount:
            # Create a debit transaction
            Transaction.objects.create(
                account=general_expenses_account,
                amount=expense_amount,
                description=form.cleaned_data['description'],
                transaction_type='debit',  # Set the transaction type
            )

            general_expenses_account.balance -= expense_amount
            general_expenses_account.save()

            form.instance.user = self.request.user
            return super().form_valid(form)
        else:
            return HttpResponseBadRequest("Insufficient balance to cover the expense.")


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense-list.html'
    context_object_name = 'expenses'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_superuser:
            # Superuser can see all data
            return Expense.objects.all()
        else:
            # Regular users can see their own data
            return Expense.objects.filter(user=self.request.user)


class TransactionListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'expenses.view_transaction'
    template_name = 'expenses/transaction-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        general_expenses_account = GeneralExpensesAccount.objects.first()

        transactions = Transaction.objects.filter(account=general_expenses_account).order_by('created_at')

        transaction_details = []

        balance = 0  # Initialize the balance

        for transaction in transactions:
            if transaction.transaction_type == 'debit':
                debit_amount = transaction.amount
                credit_amount = None
            else:
                debit_amount = None
                credit_amount = transaction.amount

            # Update the balance based on the transaction type
            if debit_amount:
                balance -= debit_amount
            else:
                balance += credit_amount

            transaction_detail = {
                'date': transaction.created_at,
                'description': transaction.description,
                'debit_amount': debit_amount,
                'credit_amount': credit_amount,
                'balance': balance,
            }
            transaction_details.append(transaction_detail)

        context['transaction_details'] = transaction_details
        return context


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense-detail.html'


class CreditAccountView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Transaction
    permission_required = 'expenses.view_transaction'
    template_name = 'expenses/credit_debit-account.html'
    fields = ['account', 'amount', 'description', 'transaction_type']  # Add the transaction_type field
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Get the submitted amount and description
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']
        transaction_type = form.cleaned_data['transaction_type']

        # Get the GeneralExpensesAccount
        general_expenses_account = GeneralExpensesAccount.objects.first()

        # Create a transaction and set the account field
        transaction = form.save(commit=False)
        transaction.account = general_expenses_account
        transaction.amount = amount
        transaction.description = description
        transaction.transaction_type = transaction_type
        transaction.save()

        if transaction_type == 'credit':
            # Credit the GeneralExpensesAccount
            general_expenses_account.credit(amount, description)
        elif transaction_type == 'debit':
            # Debit the GeneralExpensesAccount
            general_expenses_account.debit(amount, description)

        # Return the account balance template as a response
        return redirect(self.success_url)


class ElectricityListView(TemplateView):
    template_name = 'electricity/electricity-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aggregate related RecyclingOperation instances based on meter_ID
        electricity_instances = Electricity.objects.annotate(
            total_material_used=Sum('recyclingoperation__material_used'),
            total_bangori=Sum('recyclingoperation__bangori'),
            total_standard_electricity_cost=Sum('recyclingoperation__standard_electricity_cost'),
        )

        # Calculate derived fields for Electricity Consumption, Electricity Cost, and Electricity Variance
        for instance in electricity_instances:
            instance.electricity_consumption = (
                instance.meter_reading - instance.previous_meter_reading
                if instance.previous_meter_reading is not None
                else 0
            )

            # Calculate Electricity Cost based on your logic (you can add the calculation here)

            # Calculate Electricity Variance
            instance.electricity_variance = (
                instance.total_standard_electricity_cost - instance.electricity_cost
                if instance.total_standard_electricity_cost is not None
                else 0
            )

        context['electricity_details'] = electricity_instances
        return context


class ElectricityCreateView(LoginRequiredMixin, CreateView):
    model = Electricity
    fields = ['date', 'shift', 'meter_reading', 'meter_ID']
    template_name = 'electricity/create-electricity.html'
    success_url = reverse_lazy('create-recycling')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the current logged-in user

        # Get the most recent operation or initial meter reading
        previous_operation = Electricity.objects.order_by('-id').first()
        initial_meter_reading = InitialMeterReading.objects.first()

        # Calculate previous meter reading based on the most recent operation or initial reading
        if previous_operation:
            form.instance.previous_meter_reading = previous_operation.meter_reading
        elif initial_meter_reading:
            form.instance.previous_meter_reading = initial_meter_reading.initial_reading
        else:
            form.instance.previous_meter_reading = form.instance.meter_reading

        # Calculate electricity consumption considering initial meter reading
        form.instance.electricity_consumption = (
                form.instance.meter_reading - form.instance.previous_meter_reading
        )

        # Calculate electricity cost
        form.instance.electricity_cost = (
                form.instance.electricity_consumption * ElectricityConfiguration.objects.first().fixed_cost_per_unit
        )

        return super().form_valid(form)


class RecyclingCreateView(CreateView):
    model = RecyclingOperation
    fields = ['meter_ID', 'customer_serial', 'material_used', 'bangori', 'rate', 'manager', 'operator', 'packer']
    template_name = 'recycling/create-recycling.html'

    def form_valid(self, form):
        form.instance.user = self.request.user

        if self.is_valid_data(form):
            self.calculate_fields(form)
            self.update_salaries(form)
            self.update_account_payable(form)

            # Save the form and assign the object to self.object
            self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def is_valid_data(self, form):
        rate = form.cleaned_data.get('rate')
        material_used = form.cleaned_data.get('material_used')
        return rate is not None and material_used is not None

    def calculate_fields(self, form):
        form.instance.standard_electricity_cost = (
                (form.instance.material_used * form.instance.rate) / Decimal('2.37')
        )
        form.instance.amount = form.instance.rate * form.instance.material_used

        electricity_instance = form.instance.meter_ID
        if electricity_instance:
            electricity_cost = electricity_instance.electricity_cost or Decimal('0.00')
            standard_electricity_cost = form.instance.standard_electricity_cost or Decimal('0.00')
            form.instance.electricity_variance = standard_electricity_cost - electricity_cost
        else:
            form.instance.electricity_variance = None

    def update_salaries(self, form):
        manager = form.cleaned_data.get('manager')
        operator = form.cleaned_data.get('operator')
        packer = form.cleaned_data.get('packer')
        material_used = form.instance.material_used

        for role, amount_multiplier in [(manager, Decimal('3.0')), (operator, Decimal('4.0')),
                                        (packer, Decimal('3.0'))]:
            if role and material_used is not None:
                try:
                    salary_instance = {
                        manager: SalaryManager,
                        operator: SalaryOperator,
                        packer: SalaryPacker
                    }[role].objects.get_or_create(**{role.__class__.__name__.lower(): role})[0]
                    salary_instance.amount1 += material_used * amount_multiplier
                    salary_instance.save()
                except (SalaryManager.DoesNotExist, SalaryOperator.DoesNotExist, SalaryPacker.DoesNotExist):
                    pass

    # Inside the update_account_payable method:
    def update_account_payable(self, form):
        customer_serial = form.cleaned_data.get('customer_serial')
        due_date = form.cleaned_data.get('date')

        if customer_serial:
            customer = customer_serial.customer
            amount = form.instance.amount  # Assuming amount is correctly calculated in the form

            # Provide a default due_date if not available in the form
            if not due_date:
                due_date = timezone.now()  # Use the current timestamp as a default

            # Create or update the AccountPayable instance for the customer
            account_payable, created = AccountPayable.objects.get_or_create(
                customer=customer,
                defaults={'amount': amount, 'due_date': due_date}
            )

            # If the AccountPayable instance already exists, update the amount and due_date
            if not created:
                account_payable.amount += amount
                account_payable.due_date = due_date
                account_payable.save()

    def get_success_url(self):
        try:
            pk_value = Decimal(str(self.object.pk))  # Convert the pk value to a Decimal instance
            return reverse_lazy('recycling-detail2', args=[pk_value])
        except AttributeError:
            # Handle the case where self.object or self.object.pk is None
            # Redirect to an error page or another appropriate URL
            return reverse_lazy('error-page')


class CustomerMetricsView(View):
    template_name = 'recycling/customerout-detail.html'

    def get(self, request):
        # Fetch all CustomerIn instances with their associated total material_quantity
        customers = CustomerIn.objects.annotate(
            total_material_quantity=Sum('material_quantity')
        ).values('customer_serial', 'total_material_quantity')

        customer_metrics = []
        for customer in customers:
            # Fetch total material_used, total bangori for each customer_serial in RecyclingOperation
            total_material_used = RecyclingOperation.objects.filter(
                customer_serial=customer['customer_serial']
            ).aggregate(total_material_used=Sum('material_used'))['total_material_used'] or 0

            total_bangori = RecyclingOperation.objects.filter(
                customer_serial=customer['customer_serial']
            ).aggregate(total_bangori=Sum('bangori'))['total_bangori'] or 0

            # Calculate total_material_lost and percentage_lost
            material_quantity = customer['total_material_quantity']
            total_material_lost = material_quantity - total_material_used - total_bangori
            percentage_lost = (total_material_lost / material_quantity) * 100

            customer_metrics.append({
                'customer_serial': customer['customer_serial'],
                'material_quantity': material_quantity,
                'total_material_used': total_material_used,
                'total_bangori': total_bangori,
                'total_material_lost': total_material_lost,
                'percentage_lost': percentage_lost,
            })

        return render(request, self.template_name, {'customer_metrics': customer_metrics})


class RecyclingDetailView(LoginRequiredMixin, DetailView):
    model = RecyclingOperation
    template_name = 'recycling/recycling-detail2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recycling_operation = self.object

        # Calculate material_lost and percentage_lost
        material_used = recycling_operation.material_used
        bangori = recycling_operation.bangori
        material_quantity = recycling_operation.customer_serial.material_quantity
        material_lost = material_quantity - (material_used + bangori)

        if material_quantity:
            percentage_lost = (material_lost / material_quantity) * 100
        else:
            percentage_lost = 0

        # Include the calculated values in the context
        context['material_lost'] = material_lost
        context['percentage_lost'] = percentage_lost

        return context


class SalaryListView(LoginRequiredMixin, TemplateView):
    template_name = 'salary/salary-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch salaries from all three models
        managers = SalaryManager.objects.all()
        operators = SalaryOperator.objects.all()
        packers = SalaryPacker.objects.all()

        context['salaries'] = list(managers) + list(operators) + list(packers)

        # Calculate total salaries for each group
        total_manager_salary = sum(manager.amount1 for manager in managers)
        total_operator_salary = sum(operator.amount1 for operator in operators)
        total_packer_salary = sum(packer.amount1 for packer in packers)

        context['total_manager_salary'] = total_manager_salary
        context['total_operator_salary'] = total_operator_salary
        context['total_packer_salary'] = total_packer_salary

        return context


class RecyclingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RecyclingOperation
    template_name = 'recycling/recycling-list.html'
    permission_required = 'recycling.view_recycling'
    context_object_name = 'recycling'
    ordering = ['-created_at']
    paginate_by = 5  # Number of items per page

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['recycling'] = page_obj
        return context


# Accounts Payable

class PayableListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AccountPayable
    permission_required = 'payable.view_payable-list'
    template_name = 'payable/payable-list.html'  # Create a template for displaying the list
    context_object_name = 'payable'  # The variable name to use in the template for the list of payables

    def get_queryset(self):
        if self.request.user.is_superuser:
            # Superuser can see all data
            return AccountPayable.objects.all()
        else:
            # Regular users can see their own data
            return AccountPayable.objects.filter(user=self.request.user)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = 'payable/create-payment.html'
    fields = ['customer', 'amount', 'description']
    success_url = reverse_lazy('payment-list')

    def form_valid(self, form):
        # Save the Payment instance
        self.object = form.save()

        # Update the AccountPayable model
        customer = form.cleaned_data.get('customer')
        amount = form.cleaned_data.get('amount')

        # Check if there is an existing AccountPayable instance for the customer
        try:
            account_payable = AccountPayable.objects.get(customer=customer)
        except AccountPayable.DoesNotExist:
            # If no existing AccountPayable instance is found, create one
            account_payable = AccountPayable.objects.create(customer=customer, amount=0)

        # Decrease the customer's amount in AccountPayable by the payment amount
        account_payable.amount -= amount
        account_payable.save()

        # Redirect to the success URL
        return HttpResponseRedirect(self.get_success_url())


class ManagerSalaryCreateView(LoginRequiredMixin, CreateView):
    model = ManagerSalaryPayment
    template_name = 'salary/manager-salary-create.html'
    fields = ['manager', 'amount1', 'description']
    success_url = reverse_lazy('salary-list')

    def form_valid(self, form):
        manager = form.cleaned_data['manager']
        amount1 = form.cleaned_data['amount1']
        transaction_type = 'debit'  # You may want to specify the transaction type here.

        # Create a transaction for manager's salary
        general_expenses_account = GeneralExpensesAccount.objects.first()
        Transaction.objects.create(
            account=general_expenses_account,
            amount=amount1,
            description=form.cleaned_data['description'],
            transaction_type=transaction_type,
        )

        try:
            manager_salary = SalaryManager.objects.get(manager=manager)
            if transaction_type == 'debit':
                manager_salary.amount1 -= amount1
            else:
                manager_salary.amount1 += amount1
            manager_salary.save()
        except SalaryManager.DoesNotExist:
            pass

        if transaction_type == 'debit':
            general_expenses_account.balance -= amount1
        else:
            general_expenses_account.balance += amount1
        general_expenses_account.save()

        return super().form_valid(form)


class OperatorSalaryCreateView(LoginRequiredMixin, CreateView):
    model = OperatorSalaryPayment
    template_name = 'salary/operator-salary-create.html'
    fields = ['operator', 'amount1', 'description']
    success_url = reverse_lazy('salary-list')

    def form_valid(self, form):
        operator = form.cleaned_data['operator']
        amount1 = form.cleaned_data['amount1']
        transaction_type = 'debit'  # You may want to specify the transaction type here.

        # Create a transaction for manager's salary
        general_expenses_account = GeneralExpensesAccount.objects.first()
        Transaction.objects.create(
            account=general_expenses_account,
            amount=amount1,
            description=form.cleaned_data['description'],
            transaction_type=transaction_type,
        )

        try:
            operator_salary = SalaryOperator.objects.get(operator=operator)
            if transaction_type == 'debit':
                operator_salary.amount1 -= amount1
            else:
                operator_salary.amount1 += amount1
            operator_salary.save()
        except SalaryOperator.DoesNotExist:
            pass

        if transaction_type == 'debit':
            general_expenses_account.balance -= amount1
        else:
            general_expenses_account.balance += amount1
        general_expenses_account.save()

        return super().form_valid(form)


class PackerSalaryCreateView(LoginRequiredMixin, CreateView):
    model = PackerSalaryPayment
    template_name = 'salary/packer-salary-create.html'
    fields = ['packer', 'amount1', 'description']
    success_url = reverse_lazy('salary-list')

    def form_valid(self, form):
        packer = form.cleaned_data['packer']
        amount1 = form.cleaned_data['amount1']
        transaction_type = 'debit'  # You may want to specify the transaction type here.

        # Create a transaction for manager's salary
        general_expenses_account = GeneralExpensesAccount.objects.first()
        Transaction.objects.create(
            account=general_expenses_account,
            amount=amount1,
            description=form.cleaned_data['description'],
            transaction_type=transaction_type,
        )

        try:
            packer_salary = SalaryPacker.objects.get(packer=packer)
            if transaction_type == 'debit':
                packer_salary.amount1 -= amount1
            else:
                packer_salary.amount1 += amount1
            packer_salary.save()
        except SalaryPacker.DoesNotExist:
            pass

        if transaction_type == 'debit':
            general_expenses_account.balance -= amount1
        else:
            general_expenses_account.balance += amount1
        general_expenses_account.save()

        return super().form_valid(form)


class CustomerInCreateView(LoginRequiredMixin, CreateView):
    model = CustomerIn
    template_name = 'recycling/create-customerin.html'
    fields = ['customer_serial', 'customer', 'material_type', 'material_quantity', 'date']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Check if a CustomerIn instance with the same customer_serial already exists
        customer_serial = form.cleaned_data.get('customer_serial')
        existing_customerin = CustomerIn.objects.filter(customer_serial=customer_serial).first()

        if existing_customerin:
            # If it already exists, raise a validation error
            form.add_error('customer_serial', forms.ValidationError('Serial no already exists'))
            return self.form_invalid(form)
        else:
            # If it doesn't exist, create a new CustomerIn instance
            form.instance = form.save()

        return super().form_valid(form)


class CustomerOutView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CustomerIn
    permission_required = 'recycling.view_customerout_list'
    template_name = 'recycling/customerout-list.html'
    context_object_name = 'customerout_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get unique customer_serial values
        unique_customer_serials = CustomerIn.objects.values_list('customer_serial', flat=True).distinct()

        customer_recycling_data = []

        for customer_serial in unique_customer_serials:
            customer_recycling = RecyclingOperation.objects.filter(customer_serial=customer_serial)

            # Calculate material_lost for each RecyclingOperation
            for recycling in customer_recycling:
                recycling.material_lost = recycling.customer_serial.material_quantity - (
                        recycling.material_used + recycling.bangori)

            customer_recycling_data.append({
                'customer_serial': customer_serial,
                'customer_recycling': customer_recycling,
            })

        context['customer_recycling_data'] = customer_recycling_data
        return context


class FlakesInCreateView(CreateView):
    model = FlakesIn
    fields = ['date', 'serial', 'flakes_type', 'flakes_quantity', 'unit_cost']
    template_name = 'flakes/create-flakes_in.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Check if a FlakesIn instance with the same serial already exists
        serial = form.cleaned_data.get('serial')
        existing_flakesin = FlakesIn.objects.filter(serial=serial).first()

        if existing_flakesin:
            # If it already exists, raise a validation error
            form.add_error('serial', forms.ValidationError('Serial number already exists'))
            return self.form_invalid(form)

        # First, validate the form
        if not form.is_valid():
            return self.form_invalid(form)

        # Perform additional actions if the form is valid
        self.calculate_total_cost(form)
        self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def calculate_total_cost(self, form):
        flakes_quantity = form.cleaned_data.get('flakes_quantity')
        unit_cost = form.cleaned_data.get('unit_cost')

        if flakes_quantity is not None and unit_cost is not None:
            total_cost = flakes_quantity * unit_cost
            form.instance.total_cost1 = total_cost
        else:
            form.instance.total_cost1 = None

    def form_invalid(self, form):
        try:
            form.instance.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
        return super().form_invalid(form)


class FlakesInListView(ListView):
    model = FlakesIn
    template_name = 'flakes/flakes-list.html'  # Your template name
    context_object_name = 'flakesin_list'  # Variable name to access in the template
    paginate_by = 10  # Number of items per page

    def get_queryset(self):
        return FlakesIn.objects.all().order_by('-date')  # Example ordering by d


class FlakesCostCreateView(CreateView):
    model = FlakesCost
    fields = ['cost_id', 'cost_of_washing', 'cost_of_transport', 'pelleting_cost', 'other_cost', ]
    template_name = 'flakes/create-flakes_cost.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        if form.is_valid():
            self.calculate_total_cost2(form)
            self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def calculate_total_cost2(self, form):
        cost_of_washing = form.cleaned_data.get('cost_of_washing')
        cost_of_transport = form.cleaned_data.get('cost_of_transport')
        pelleting_cost = form.cleaned_data.get('pelleting_cost')
        other_cost = form.cleaned_data.get('other_cost')

        # Check if all costs are valid numbers before calculating total_cost2
        if all(isinstance(cost, (int, float, Decimal)) for cost in
               [cost_of_washing, cost_of_transport, pelleting_cost, other_cost]):
            total_cost = cost_of_washing + cost_of_transport + pelleting_cost + other_cost
            form.instance.total_cost2 = total_cost
        else:
            form.instance.total_cost2 = None

    def form_invalid(self, form):
        try:
            form.instance.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
        return super().form_invalid(form)


class PelletsPriceCreateView(CreateView):
    model = PelletsPrice
    fields = ['date', 'serial', 'cost_id', 'pellets_quantity', 'unit_price', ]
    template_name = 'flakes/create-pellets_price.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        if form.is_valid():
            self.calculate_flakes_profit(form)
            self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def calculate_flakes_profit(self, form):
        pellets_quantity = form.cleaned_data.get('pellets_quantity')
        unit_price = form.cleaned_data.get('unit_price')

        if pellets_quantity is not None and unit_price is not None:
            price = pellets_quantity * unit_price
            form.instance.price = price
        else:
            form.instance.price = None

        serial_instance = form.instance.serial
        if serial_instance:
            total_cost1 = serial_instance.total_cost1 or Decimal('0.00')
            flakes_cost_instance = form.instance.cost_id
            if flakes_cost_instance:
                total_cost2 = flakes_cost_instance.total_cost2 or Decimal('0.00')
                form.instance.profit = price - (total_cost1 + total_cost2)
            else:
                form.instance.profit = None
        else:
            form.instance.profit = None

    def form_invalid(self, form):
        try:
            form.instance.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
        return super().form_invalid(form)


class PelletsPriceListView(ListView):
    model = PelletsPrice
    template_name = 'flakes/pellets-list.html'  # Your template name
    context_object_name = 'pellets_prices'  # Variable name to access in the template
    paginate_by = 10  # Number of items per page

    def get_queryset(self):
        # Customize the queryset if needed (filtering, ordering, etc.)
        return PelletsPrice.objects.all().order_by('-date')  # Example ordering by date

    def get_queryset(self):
        if self.request.user.is_superuser:
            # Superuser can see all data
            return PelletsPrice.objects.all().order_by('-date')
        else:
            # Regular users can see their own data
            return PelletsPrice.objects.filter(user=self.request.user)