import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self):
        post_migrate.connect(create_default_categories, sender=self)
        post_migrate.connect(create_default_account, sender=self)

def create_default_categories(sender, **kwargs):
    from .models.base import TransactionCategory
    default_categories = [
        {"name": "Transfer Expense", "transaction_type": "expense"},
        {"name": "Transfer Income", "transaction_type": "income"},
        {"name": "Transfer Commission", "transaction_type": "expense"},
    ]

    for category_data in default_categories:
        try:
            TransactionCategory.objects.get_or_create(**category_data)
        except (OperationalError, ProgrammingError) as e:
            # Logga un messaggio di errore se le tabelle non sono pronte
            logger.error("Could not create default transaction categories. "
                         "This might be due to the tables not being ready. "
                         "Error: %s", e)


def create_default_account(sender, **kwargs):
    from .models.base import Account
    
    # Definizione dei dati dell'account di default
    default_account = {
        "name": "Contanti",
        "account_type": "cash",
        "institution": "None",
        "initial_balance": 0,
    }

    try:
        # Controlla se esiste già almeno un oggetto Account
        if not Account.objects.exists():
            # Crea l'account di default se nessun account è presente
            Account.objects.get_or_create(**default_account)
            logger.info("Default account created successfully.")
    except (OperationalError, ProgrammingError) as e:
        # Logga un messaggio di errore se le tabelle non sono pronte o c'è un altro problema
        logger.error(
            "Could not create default account. "
            "This might be due to the tables not being ready. "
            "Error: %s", e
        )
