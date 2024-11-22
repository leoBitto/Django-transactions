from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Avg, Count, Q
from decimal import Decimal

class DailyTransactionAggregation(DailyAggregationBase):
    """
    Aggregazione giornaliera delle transazioni per account, categoria e tipo
    """
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='daily_aggregations'
    )
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.CASCADE, 
        related_name='daily_aggregations',
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=7, 
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name=_("Tipo di Transazione")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Totale Importo")
    )
    transaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Numero di Transazioni")
    )
    average_transaction_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        verbose_name=_("Media Importo Transazioni")
    )

    class Meta(DailyAggregationBase.Meta):
        unique_together = ['date', 'account', 'category', 'transaction_type']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['account']),
            models.Index(fields=['category']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date', 'account']),
            models.Index(fields=['date', 'category']),
            models.Index(fields=['date', 'transaction_type']),
        ]
        verbose_name = _("Aggregazione Giornaliera Transazioni")
        verbose_name_plural = _("Aggregazioni Giornaliere Transazioni")

    @classmethod
    def aggregate_transactions(cls, start_date=None, end_date=None):
        """
        Metodo per aggregare le transazioni in modo automatico
        """
        # Prepara il queryset base delle transazioni
        transactions = Transaction.objects.all()
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        # Aggrega per data, account, categoria e tipo transazione
        aggregations = transactions.values(
            'date', 'account', 'category', 'transaction_type'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_transaction_amount=Avg('amount')
        )

        # Crea o aggiorna gli oggetti di aggregazione
        for agg in aggregations:
            cls.objects.update_or_create(
                date=agg['date'],
                account_id=agg['account'],
                category_id=agg['category'],
                transaction_type=agg['transaction_type'],
                defaults={
                    'total_amount': agg['total_amount'] or Decimal('0'),
                    'transaction_count': agg['transaction_count'],
                    'average_transaction_amount': agg['average_transaction_amount']
                }
            )


class WeeklyTransactionAggregation(WeeklyAggregationBase):
    """
    Aggregazione settimanale delle transazioni per account, categoria e tipo
    """
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='weekly_aggregations'
    )
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.CASCADE, 
        related_name='weekly_aggregations',
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=7, 
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name=_("Tipo di Transazione")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Totale Importo")
    )
    transaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Numero di Transazioni")
    )
    average_transaction_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        verbose_name=_("Media Importo Transazioni")
    )

    class Meta(WeeklyAggregationBase.Meta):
        unique_together = ['year', 'week', 'account', 'category', 'transaction_type']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['week']),
            models.Index(fields=['account']),
            models.Index(fields=['category']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['year', 'week']),
            models.Index(fields=['year', 'account']),
            models.Index(fields=['year', 'category']),
            models.Index(fields=['year', 'transaction_type']),
        ]
        verbose_name = _("Aggregazione Settimanale Transazioni")
        verbose_name_plural = _("Aggregazioni Settimanali Transazioni")

    @classmethod
    def aggregate_transactions(cls, year=None, week=None):
        """
        Metodo per aggregare le transazioni settimanalmente
        """
        from django.db.models import F
        from datetime import date
        import calendar

        # Prepara il queryset base delle transazioni
        transactions = Transaction.objects.all()
        
        if year:
            transactions = transactions.filter(date__year=year)
        if week:
            # Calcola l'intervallo di date per la settimana specificata
            start_date = date(year, 1, 1) + timedelta(weeks=week-1)
            end_date = start_date + timedelta(days=6)
            transactions = transactions.filter(date__range=[start_date, end_date])

        # Aggrega per anno, settimana, account, categoria e tipo transazione
        aggregations = transactions.annotate(
            year=F('date__year'),
            week=F('date__week')
        ).values(
            'year', 'week', 'account', 'category', 'transaction_type'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_transaction_amount=Avg('amount')
        )

        # Crea o aggiorna gli oggetti di aggregazione
        for agg in aggregations:
            cls.objects.update_or_create(
                year=agg['year'],
                week=agg['week'],
                account_id=agg['account'],
                category_id=agg['category'],
                transaction_type=agg['transaction_type'],
                defaults={
                    'total_amount': agg['total_amount'] or Decimal('0'),
                    'transaction_count': agg['transaction_count'],
                    'average_transaction_amount': agg['average_transaction_amount']
                }
            )


class MonthlyTransactionAggregation(MonthlyAggregationBase):
    """
    Aggregazione mensile delle transazioni per account, categoria e tipo
    """
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='monthly_aggregations'
    )
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.CASCADE, 
        related_name='monthly_aggregations',
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=7, 
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name=_("Tipo di Transazione")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Totale Importo")
    )
    transaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Numero di Transazioni")
    )
    average_transaction_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        verbose_name=_("Media Importo Transazioni")
    )

    class Meta(MonthlyAggregationBase.Meta):
        unique_together = ['year', 'month', 'account', 'category', 'transaction_type']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['month']),
            models.Index(fields=['account']),
            models.Index(fields=['category']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['year', 'month']),
            models.Index(fields=['year', 'account']),
            models.Index(fields=['year', 'category']),
            models.Index(fields=['year', 'transaction_type']),
        ]
        verbose_name = _("Aggregazione Mensile Transazioni")
        verbose_name_plural = _("Aggregazioni Mensili Transazioni")

    @classmethod
    def aggregate_transactions(cls, year=None, month=None):
        """
        Metodo per aggregare le transazioni mensilmente
        """
        from django.db.models import F

        # Prepara il queryset base delle transazioni
        transactions = Transaction.objects.all()
        
        if year:
            transactions = transactions.filter(date__year=year)
        if month:
            transactions = transactions.filter(date__month=month)

        # Aggrega per anno, mese, account, categoria e tipo transazione
        aggregations = transactions.annotate(
            year=F('date__year'),
            month=F('date__month')
        ).values(
            'year', 'month', 'account', 'category', 'transaction_type'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_transaction_amount=Avg('amount')
        )

        # Crea o aggiorna gli oggetti di aggregazione
        for agg in aggregations:
            cls.objects.update_or_create(
                year=agg['year'],
                month=agg['month'],
                account_id=agg['account'],
                category_id=agg['category'],
                transaction_type=agg['transaction_type'],
                defaults={
                    'total_amount': agg['total_amount'] or Decimal('0'),
                    'transaction_count': agg['transaction_count'],
                    'average_transaction_amount': agg['average_transaction_amount']
                }
            )


class QuarterlyTransactionAggregation(QuarterlyAggregationBase):
    """
    Aggregazione trimestrale delle transazioni per account, categoria e tipo
    """
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='quarterly_aggregations'
    )
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.CASCADE, 
        related_name='quarterly_aggregations',
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=7, 
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name=_("Tipo di Transazione")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Totale Importo")
    )
    transaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Numero di Transazioni")
    )
    average_transaction_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        verbose_name=_("Media Importo Transazioni")
    )

    class Meta(QuarterlyAggregationBase.Meta):
        unique_together = ['year', 'quarter', 'account', 'category', 'transaction_type']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['quarter']),
            models.Index(fields=['account']),
            models.Index(fields=['category']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['year', 'quarter']),
            models.Index(fields=['year', 'account']),
            models.Index(fields=['year', 'category']),
            models.Index(fields=['year', 'transaction_type']),
        ]
        verbose_name = _("Aggregazione Trimestrale Transazioni")
        verbose_name_plural = _("Aggregazioni Trimestrali Transazioni")

    @classmethod
    def aggregate_transactions(cls, year=None, quarter=None):
        """
        Metodo per aggregare le transazioni trimestralmente
        """
        from django.db.models import F

        # Prepara il queryset base delle transazioni
        transactions = Transaction.objects.all()
        
        if year:
            transactions = transactions.filter(date__year=year)
        if quarter:
            # Calcola l'intervallo di mesi per il trimestre
            quarter_months = {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12]
            }
            transactions = transactions.filter(date__month__in=quarter_months.get(quarter, []))

        # Aggrega per anno, trimestre, account, categoria e tipo transazione
        aggregations = transactions.annotate(
            year=F('date__year'),
            quarter=F('date__quarter')
        ).values(
            'year', 'quarter', 'account', 'category', 'transaction_type'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_transaction_amount=Avg('amount')
        )

        # Crea o aggiorna gli oggetti di aggregazione
        for agg in aggregations:
            cls.objects.update_or_create(
                year=agg['year'],
                quarter=agg['quarter'],
                account_id=agg['account'],
                category_id=agg['category'],
                transaction_type=agg['transaction_type'],
                defaults={
                    'total_amount': agg['total_amount'] or Decimal('0'),
                    'transaction_count': agg['transaction_count'],
                    'average_transaction_amount': agg['average_transaction_amount']
                }
            )


class YearlyTransactionAggregation(YearlyAggregationBase):
    """
    Aggregazione annuale delle transazioni per account, categoria e tipo
    """
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='yearly_aggregations'
    )
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.CASCADE, 
        related_name='yearly_aggregations',
        null=True,
        blank=True
    )
    # transaction_type = models.CharField(
    #     max_length=7, 
    #     choices=Transaction.TRANSACTION_TYPES,