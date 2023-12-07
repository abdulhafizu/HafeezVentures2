from django.urls import path, register_converter
from .converters import DecimalConverter

register_converter(DecimalConverter, 'decimal')

from .views import (HomePageView,
                    ExpenseCreateView,
                    ExpenseListView,
                    ExpenseDetailView,
                    RecyclingCreateView,
                    RecyclingDetailView,
                    RecyclingListView,
                    PayableListView,
                    PaymentCreateView,
                    SalaryListView,
                    ManagerSalaryCreateView, CreditAccountView, TransactionListView, CustomerInCreateView,
                    CustomerOutView, OperatorSalaryCreateView,
                    PackerSalaryCreateView, CustomLoginView, ElectricityCreateView, ElectricityListView,
                    CustomerMetricsView, PelletsPriceListView, FlakesCostCreateView, FlakesInCreateView,
                    PelletsPriceCreateView, FlakesInListView,
                    )

register_converter(DecimalConverter, 'decimal')

urlpatterns = [
    path('flakes/pellets-list/', PelletsPriceListView.as_view(), name='pellets-list'),
    path('flakes/flakes-list/', FlakesInListView.as_view(), name='flakes-list'),
    path('flakes/create-flakes_cost/', FlakesCostCreateView.as_view(), name='create-flakes_cost'),
    path('flakes/create-flakes_in/', FlakesInCreateView.as_view(), name='create-flakes_in'),
    path('flakes/create-pellets_price/', PelletsPriceCreateView.as_view(), name='create-pellets_price'),
    path('recycling/customeroutdetail/', CustomerMetricsView.as_view(), name='customerout-detail'),
    path('recycling/customerout/', CustomerOutView.as_view(), name='customerout-list'),
    path('recycling/<decimal:pk>/', RecyclingDetailView.as_view(), name='recycling-detail2'),
    path('recycling/createcustomerin/', CustomerInCreateView.as_view(), name='create-customerin'),
    path('expenses/transaction-list/', TransactionListView.as_view(), name='transaction-list'),
    path('expenses/credit_debit-account/', CreditAccountView.as_view(), name='credit_debit-account'),
    path('salary/create_manager_salary/', ManagerSalaryCreateView.as_view(), name='manager-salary-create'),
    path('salary/create_operator_salary/', OperatorSalaryCreateView.as_view(), name='operator-salary-create'),
    path('salary/create_packer_salary/', PackerSalaryCreateView.as_view(), name='packer-salary-create'),
    path('salary/', SalaryListView.as_view(), name='salary-list'),
    path('payable/', PayableListView.as_view(), name='payable-list'),
    path('recycling/create/', RecyclingCreateView.as_view(), name='create-recycling'),
    path('electricity/create/', ElectricityCreateView.as_view(), name='create-electricity'),
    path('electricity/electricity-list/', ElectricityListView.as_view(), name='electricity-list'),
    path('recycling/', RecyclingListView.as_view(), name='recycling-list'),
    path('expenses/create/', ExpenseCreateView.as_view(), name='create-expense'),
    path('payable/create/', PaymentCreateView.as_view(), name='create-payment'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('payable/<int:pk>/', ExpenseDetailView.as_view(), name='payment-detail'),
    path('payable/', PayableListView.as_view(), name='payment-list'),
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('', CustomLoginView.as_view(), name='login'),
    path('index', HomePageView.as_view(), name='index'),

]