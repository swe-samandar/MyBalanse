from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Account, IncomeCategory, ExpenseCategory, Income, Expense
from .forms import AccountForm, IncomeCategoryForm, ExpenseCategoryForm, IncomeForm, ExpenseForm

# Create your views here.

class MainView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:main'
    
    def get(self, request):
        incomes = Income.objects.filter(user=request.user)
        expenses = Expense.objects.filter(user=request.user)
        accounts = Account.objects.filter(user=request.user)
        total_income, total_expense, total_balance = 0, 0, 0
        for income in incomes:
            total_income += income.amount
        for expense in expenses:
            total_expense += expense.amount
        for account in accounts:
            total_balance += account.amount
        
        context = {
            'incomes': incomes,
            'expenses': expenses,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
        }
        return render(request, 'main/main.html', context)


class TransactionsView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:transactions'

    def get(self, request):
        accounts = Account.objects.filter(user=request.user)
        incomes = Income.objects.filter(user=request.user)
        expenses = Expense.objects.filter(user=request.user)
        transactions = [income for income in incomes] + [expense for expense in expenses]
        context = {
            'accounts': accounts,
            'transactions': transactions,
        }
        return render(request, 'main/transactions.html', context)
    

class IncomeView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:income'

    def get(self, request):
        incomes = Income.objects.filter(user=request.user)
        total_income = sum(income.amount for income in incomes)
        context = {
            'incomes': incomes,
            'total_income': total_income,
        }
        return render(request, 'main/income.html', context)


class ExpensesView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:expenses'

    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        total_expense = sum(expense.amount for expense in expenses)
        context = {
            'expenses': expenses,
            'total_expense': total_expense,
        }
        return render(request, 'main/expenses.html', context)
    

class NewAccountView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:new_account'

    def get(self, request):
        form = AccountForm()
        return render(request, 'main/new_account.html', {'form': form})
    
    def post(self, request):
        form = AccountForm(request.POST, request.FILES)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('main:transactions')
        return render(request, 'main/new_account.html', {'form': form})


class NewIncomeView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:new_income'

    def get(self, request):
        form = IncomeForm()
        return render(request, 'main/new_income.html', {'form': form})
    
    def post(self, request):
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:income')
        return render(request, 'main/new_income.html', {'form': form})
        
    
class NewExpenseView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:new_expense'

    def get(self, request):
        form = ExpenseForm()
        return render(request, 'main/new_expense.html', {'form': form})
    
    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:expenses')
        return render(request, 'main/new_expense.html', {'form': form})
    

class UpdateAccountView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:update_account'

    def get(self, request, account_id):
        account = get_object_or_404(Account, id=account_id)
        form = AccountForm(instance=account)
        return render(request, 'main/update_account.html', {'form': form})
    
    def post(self, request, account_id):
        account = get_object_or_404(Account, id=account_id)
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            account = form.save()
            return redirect('main:transactions')
        return render(request, 'main:update_account.html', {'form': form})
    

class UpdateIncomeView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:update_income'

    def get(self, request, account_id):
        account = get_object_or_404(Income, id=account_id)
        form = IncomeForm(instance=account)
        return render(request, 'main/update_income.html', {'form': form})
    
    def post(self, request, account_id):
        account = get_object_or_404(Income, id=account_id)
        form = IncomeForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            account = form.save()
            return redirect('main:income')
        return render(request, 'main:update_income.html', {'form': form})
    

class UpdateExpenseView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:update_expense'

    def get(self, request, account_id):
        account = get_object_or_404(Expense, id=account_id)
        form = ExpenseForm(instance=account)
        return render(request, 'main/update_expense.html', {'form': form})
    
    def post(self, request, account_id):
        account = get_object_or_404(Expense, id=account_id)
        form = ExpenseForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            account = form.save()
            return redirect('main:expenses')
        return render(request, 'main:update_expense.html', {'form': form})


class DeleteAccountView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:delete_account'


class DeleteIncomeView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:delete_income'


class DeleteExpenseView(LoginRequiredMixin, View):
    login_url = 'users:login'
    next = 'main:delete_expense'