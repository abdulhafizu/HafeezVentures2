from django.contrib import admin
from .models import ExpenseCategory, Expense, Customer, RecyclingOperation, AccountPayable, Payment, Operator, \
    Manager, Packer, ElectricityConfiguration, SalaryManager, SalaryOperator, SalaryPacker, GeneralExpensesAccount, \
    CustomerIn, InitialMeterReading, Electricity, Transaction, FlakesIn, FlakesCost, PelletsPrice


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'category', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'description')


@admin.register(Operator)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address')


@admin.register(Manager)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address')


@admin.register(Packer)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address')


admin.site.register(RecyclingOperation)
admin.site.register(ElectricityConfiguration)
admin.site.register(Customer)
admin.site.register(Payment)
admin.site.register(AccountPayable)
admin.site.register(SalaryManager)
admin.site.register(SalaryOperator)
admin.site.register(SalaryPacker)
admin.site.register(GeneralExpensesAccount)
admin.site.register(CustomerIn)
admin.site.register(InitialMeterReading)
admin.site.register(Electricity)
admin.site.register(Transaction)
admin.site.register(FlakesIn)
admin.site.register(FlakesCost)
admin.site.register(PelletsPrice)