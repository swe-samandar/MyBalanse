from django.urls import path
from .views import (
    MainView,
    TransactionsView,
    IncomeView,
    ExpensesView,
    NewAccountView,
    NewIncomeView,
    NewExpenseView,
    UpdateAccountView, 
    UpdateIncomeView,
    UpdateExpenseView,
    DeleteAccountView,
    DeleteIncomeView,
    DeleteExpenseView,
)

app_name = 'main'

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('transactions', TransactionsView.as_view(), name='transactions'),
    path('income', IncomeView.as_view(), name='income'),
    path('expenses', ExpensesView.as_view(), name='expenses'),
    path('new-account', NewAccountView.as_view(), name='new_account'),
    path('new-income', NewIncomeView.as_view(), name='new_income'),
    path('new-expense', NewExpenseView.as_view(), name='new_expense'),
    path('<int:account_id>/update-account', UpdateAccountView.as_view(), name='update_account'),
    path('<int:income_id>/update-income', UpdateIncomeView.as_view(), name='update_income'),
    path('<int:expense_id>/update-expense', UpdateExpenseView.as_view(), name='update_expense'),
    path('<int:account_id>delete-account', DeleteAccountView.as_view(), name='delete_account'),
    path('<int:income_id>/delete-income', DeleteIncomeView.as_view(), name='delete_income'),
    path('<int:expense_id>/delete-expense', DeleteExpenseView.as_view(), name='delete_expense'),
]