from django import forms
from .models import *
from django.forms.widgets import SelectDateWidget
try:
    from screener.models import Company
except ModuleNotFoundError:
    Company = 'self'  # O qualsiasi altro gestore che desideri in caso di mancanza dell'applicazione


class RecurringTransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    frequency = forms.ChoiceField(choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ])
    type = forms.ChoiceField(choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget, required=False)
    description = forms.CharField(max_length=100, required=False)
    payment_method = forms.CharField()
    income_type = forms.ChoiceField(choices=Income.Choices)
    expenditure_type = forms.ChoiceField(choices=Expenditure.Choices)


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'time', 'amount', 'description', 'type', 'bank_account', 'cash']

    error_messages = {
        'date': {'invalid': 'Please enter a valid date.', 'required': 'This field is required.'},
        'time': {'invalid': 'Please enter a valid time.', 'required': 'This field is required.'},
        'type': {'required': 'Please select the expenditure type.'},
        'amount': {'invalid': 'Please enter a valid amount.', 'required': 'This field is required.'},
        'bank_account': {'required': 'Please select a bank account.'},
        'cash': {'required': 'Please select a cash entity.'},
    }

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['date', 'time', 'amount', 'description', 'type', 'bank_account', 'cash']

    error_messages = {
        'date': {'invalid': 'Please enter a valid date.', 'required': 'This field is required.'},
        'time': {'invalid': 'Please enter a valid time.', 'required': 'This field is required.'},
        'type': {'required': 'Please select the expenditure type.'},
        'amount': {'invalid': 'Please enter a valid amount.', 'required': 'This field is required.'},
        'bank_account': {'required': 'Please select a bank account.'},
        'cash': {'required': 'Please select a cash entity.'},
    }

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.all())


class AddBankForm(forms.Form):
    name = forms.CharField()
    balance = forms.DecimalField(max_digits=10, decimal_places=2)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
        

class AddCashAmountForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
 
class ManageCashForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = forms.ChoiceField(choices=[('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw')])
    commission = forms.DecimalField(max_digits=10, decimal_places=2)






