from django import forms
from .models.base import Account, Transaction, TransactionCategory


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'institution', 'initial_balance', 'is_active']
        labels = {
            'name': 'Nome del Conto',
            'account_type': 'Tipo di Conto',
            'institution': 'Istituzione',
            'initial_balance': 'Bilancio Iniziale',
            'is_active': 'Attivo',
        }
        widgets = {
            'initial_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'description', 'transaction_type', 'category', 'account']
        labels = {
            'date': 'Data',
            'amount': 'Importo',
            'description': 'Descrizione',
            'transaction_type': 'Tipo di Transazione',
            'category': 'Categoria',
            'account': 'Conto Associato',
        }
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'account': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        amount = cleaned_data.get('amount')

        if category and transaction_type and category.transaction_type != transaction_type:
            self.add_error('category', "La categoria deve corrispondere al tipo di transazione.")

        if amount and amount <= 0:
            self.add_error('amount', "L'importo deve essere maggiore di zero.")

        return cleaned_data


class TransferFundsForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01,
        label='Importo', widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    source_fund = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        label='Conto di Origine',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination_fund = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        label='Conto di Destinazione',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    commission = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, initial=0.00,
        label='Commissione', widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        source_fund = cleaned_data.get('source_fund')
        destination_fund = cleaned_data.get('destination_fund')
        commission = cleaned_data.get('commission') or 0

        if source_fund == destination_fund:
            self.add_error('destination_fund', "I conti di origine e di destinazione non possono coincidere.")

        if source_fund and source_fund.current_balance() < (amount + commission):
            raise forms.ValidationError("Fondi insufficienti per coprire l'importo e la commissione.")

        return cleaned_data


class TransactionCategoryForm(forms.ModelForm):
    class Meta:
        model = TransactionCategory
        fields = ['name', 'description', 'transaction_type', 'parent']
        labels = {
            'name': 'Nome della Categoria',
            'description': 'Descrizione',
            'transaction_type': 'Tipo',
            'parent': 'Categoria Principale',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'transaction_type' in self.data:
            transaction_type = self.data.get('transaction_type')
            self.fields['parent'].queryset = TransactionCategory.objects.filter(transaction_type=transaction_type)
        elif self.instance.pk:
            self.fields['parent'].queryset = TransactionCategory.objects.filter(transaction_type=self.instance.transaction_type)


class RecurringTransactionForm(forms.Form):
    FREQUENCY_CHOICES = [
        ('daily', 'Giornaliera'),
        ('weekly', 'Settimanale'),
        ('monthly', 'Mensile'),
        ('semi-annual', 'Semestrale'),
        ('annual', 'Annuale'),
    ]
    
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01,
        label='Importo', widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label='Descrizione', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        label='Tipo di Transazione', widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=TransactionCategory.objects.all(),
        label='Categoria', widget=forms.Select(attrs={'class': 'form-control'})
    )
    account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        label='Conto Associato', widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label='Data di Inizio', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label='Data di Fine', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False
    )
    frequency = forms.ChoiceField(
        choices=FREQUENCY_CHOICES,
        label='Frequenza', widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and end_date <= start_date:
            self.add_error('end_date', "La data di fine deve essere successiva alla data di inizio.")

        return cleaned_data
