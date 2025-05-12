from django.contrib import admin
from .models import Account, IncomeCategory, ExpenseCategory, Income, Expense

# Register your models here.

admin.site.register([Account, IncomeCategory, ExpenseCategory, Income, Expense])