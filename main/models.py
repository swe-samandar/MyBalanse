from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CurrencyChoices(models.TextChoices):
    UZS = 'UZS', _("Uzbek so'm")
    USD = 'USD', _("US Dollar")
    RUB = 'RUB', _("Russian Ruble")
    EURO = 'EURO', _("Euro")

class Account(models.Model):   
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    type = models.CharField(max_length=150)
    currency_type = models.TextField(max_length=4, choices=CurrencyChoices.choices, default=CurrencyChoices.UZS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=1024, blank=True, null=True)
    image = models.ImageField(upload_to='accounts/', default='accounts/default.png')

    def __str__(self):
        return self.type


class IncomeCategory(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='incomes/', default='incomes/default.png')

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='expenses/', default='expenses/default.png')

    def __str__(self):
        return self.name
    

class Income(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField()
    description = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['-date']


class Expense(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField()
    description = models.CharField(max_length=1024, blank=True, null=True)


    class Meta:
        ordering = ['-date']