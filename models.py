from django.db import models
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
try:
    from screener.models import Company
except ModuleNotFoundError:
    Company = 'self'  # O qualsiasi altro gestore che desideri in caso di mancanza dell'applicazione


class BankAccount(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()

    # funzione per trasferire denaro da questo account a un altro account bancario
    def transfer_money(self, target_account, amount, commission):
        if self.balance >= (amount + commission):
            self.balance -= (amount + commission)
            target_account.balance += amount
            self.save()
            target_account.save()
            return True
        return False

    # funzione per ritirare denaro dall'account
    def withdraw_money(self, target_account, amount, commision):
        if self.balance >= (amount + commision):
            self.balance -= (amount + commision)
            target_account.amount += amount
            self.save()
            target_account.save()
            return True
        return False

    @property
    def total_balance(self):
        today = date.today()
        transactions = self.transactions.filter(processed_date__range=(self.start_date, today))
        return sum(transactions.values_list('amount', flat=True))

    def __str__(self):
        return f"{self.name}"
    
class Cash(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()

    @property
    def total_amount(self):
        today = date.today()
        transactions = self.transactions.filter(processed_date__range=(self.start_date, today))
        return sum(transactions.values_list('amount', flat=True))

    def __str__(self):
        return f"{self.amount} - Cash"

class BalanceLog(models.Model):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class AmountLog(models.Model):
    cash = models.ForeignKey(Cash, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=BankAccount)
def log_balance_change(sender, instance, created, **kwargs):
    if not created:
        BalanceLog.objects.create(bank_account=instance, balance=instance.balance)

@receiver(post_save, sender=Cash)
def log_amount_change(sender, instance, created, **kwargs):
    if not created:
        AmountLog.objects.create(cash=instance, amount=instance.amount)

class Transaction(models.Model):
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.ForeignKey(BankAccount, null=True, blank=True, on_delete=models.CASCADE)
    cash = models.ForeignKey(Cash, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction: {self.amount} on {self.date}"

    def save(self, *args, **kwargs):
        # Implementa una regola di business (ad esempio, verifica che l'importo sia positivo)
        if self.amount <= 0:
            raise ValueError("amount must be more than zero.")
        
        super().save(*args, **kwargs)

class Income(Transaction):
    Choices =(
        ('Savings','Savings'),
        ('Salary','Salary'),
        ('Bonus','Bonus'),
        ('Dividends','Dividends'),
        ('Freelance', 'Freelance'), 
        ('Investment', 'Investment'),
        ('Other','Other'),
    )
    type=models.CharField(choices=Choices, max_length=10)

    def __str__(self):
        return f"Income: {self.amount} on {self.date}"

class Expenditure(Transaction):
    Choices =(
        ('Food','Food'),
        ('Gifts','Gifts'),
        ('Health','Health'),
        ('House','House'),
        ('Transport','Transport'),
        ('Personal Expense','Personal Expense'),
        ('Bills','Bills'),
        ('Trip','Trip'),
        ('Debts','Debts'),
        ('Entertainment', 'Entertainment'), 
        ('Education', 'Education'), 
        ('Clothing', 'Clothing'), 
        ('Other','Other'),
    )
    type=models.CharField(choices=Choices, max_length=16)

    def __str__(self):
        return f"Expenditure: {self.amount} on {self.date}"

class Portfolio(BankAccount):
    related_stocks = models.ManyToManyField('StockInPortfolio', blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Calcola e crea un nuovo log ogni volta che il portafoglio viene salvato
        PortfolioValueLog.objects.create(portfolio=self, value=self.total_value)

    @property
    def total_value(self):
        # Calcola la somma del saldo e del valore delle azioni
        return int(self.balance) + self.stock_value

    @property
    def stock_value(self):
        # Calcola il valore totale delle azioni nel portafoglio
        return sum(stock.price * stock.quantity for stock in self.related_stocks.all())
    
class PortfolioValueLog(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.portfolio.name} - {self.date} - {self.value}"

class StockInPortfolio(models.Model):
    #company = models.ForeignKey(Company, on_delete=models.CASCADE)
    related_portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    def __str__(self):
        return f"{self.company.name} - {self.quantity} - {self.price}"

class StockTransaction(models.Model):
    stock = models.ForeignKey(StockInPortfolio, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=5, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity}"










