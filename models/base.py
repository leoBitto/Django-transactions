from django.db import models
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Conto Corrente'),
        ('savings', 'Conto Risparmio'),
        ('deposit', 'Deposito'),
        ('cash', 'Contanti'),
    )

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    institution = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['account_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    def get_balance_at_date(self, target_date=None):
        if target_date is None:
            target_date = date.today()

        # Ottimizziamo la query usando annotate e aggregate
        balance = self.initial_balance

        transactions_sum = self.account_transactions.filter(
            date__lte=target_date
        ).aggregate(
            income_sum=Sum('amount', filter=models.Q(transaction_type='income')),
            expense_sum=Sum('amount', filter=models.Q(transaction_type='expense'))
        )

        # Gestiamo il caso in cui non ci sono transazioni (None)
        income = transactions_sum['income_sum'] or Decimal('0')
        expenses = transactions_sum['expense_sum'] or Decimal('0')
        
        return balance + income - expenses

    def current_balance(self):
        return self.get_balance_at_date()

    # Metodo per calcolare il saldo giornaliero
    def get_daily_balances(self):
        # Iniziamo dal saldo iniziale
        daily_balances = {}

        # Recuperiamo tutte le transazioni legate all'account, filtrate per data e tipo
        transactions = Transaction.objects.filter(
            account=self
        ).values('date').annotate(
            total_income=Sum('amount', filter=Q(transaction_type='income')),
            total_expense=Sum('amount', filter=Q(transaction_type='expense'))
        ).order_by('date')

        # Iniziamo a calcolare i bilanci giorno per giorno
        balance = self.initial_balance  # Parte dal bilancio iniziale
        for transaction in transactions:
            # Calcoliamo il saldo del giorno in base al totale delle transazioni
            daily_balance = balance + (transaction['total_income'] or 0) - (transaction['total_expense'] or 0)
            daily_balances[transaction['date']] = daily_balance
            # Aggiorniamo il bilancio accumulato
            balance = daily_balance

        return daily_balances

class TransactionCategory(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Entrata'),
        ('expense', 'Uscita'),
    )

    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.PROTECT
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

    def get_hierarchy(self, n=None):
        """
        Restituisce una lista con la gerarchia dei parent fino all'oggetto corrente.
        Se `n` è specificato, limita la lista ai primi `n` parent.
        """
        hierarchy = []
        category = self
        while category:
            hierarchy.insert(0, category)  # Inserisce il parent corrente all'inizio della lista
            if n and len(hierarchy) == n:
                break
            category = category.parent
        return hierarchy
    
    def get_hierarchy_limited(self):
        return self.get_hierarchy(3)



class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Entrata'),
        ('expense', 'Uscita'),
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='account_transactions'
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.PROTECT,
        related_name='category_transactions'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['account', 'date', 'transaction_type']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.date} - {self.amount} € - {self.category}"

    def clean(self):
        if self.category and self.category.transaction_type != self.transaction_type:
            raise ValidationError({
                'category': 'La categoria deve essere dello stesso tipo della transazione'
            })
        if self.amount <= 0:
            raise ValidationError({
                'amount': 'L\'importo deve essere maggiore di zero'
            })
            