from django import forms
from .models import Account, IncomeCategory, ExpenseCategory, Income, Expense

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['type']


class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ['name', 'image']


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'image']

    
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['category', 'account_type', 'amount', 'date', 'description']


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'account_type', 'amount', 'date', 'description']