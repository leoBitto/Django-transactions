from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models.base import Account, Transaction, TransactionCategory
from django.core.exceptions import ValidationError


class AccountTransactionsTestCase(TestCase):
    def setUp(self):
        # Create categories for income and expense
        self.income_category = TransactionCategory.objects.create(
            name="Salary", 
            transaction_type="income"
        )
        self.expense_category = TransactionCategory.objects.create(
            name="Groceries", 
            transaction_type="expense"
        )
        
        # Create a test account
        self.account = Account.objects.create(
            name="Test Account",
            account_type="checking",
            initial_balance=Decimal('1000.00'),
            institution="Test Bank"
        )

    def test_initial_balance(self):
        """Test that the initial balance is correctly set."""
        self.assertEqual(self.account.get_balance_at_date(), Decimal('1000.00'))

    def test_single_income_transaction(self):
        """Verify that an income transaction correctly updates the balance."""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('500.00'),
            transaction_type="income",
            category=self.income_category
        )
        self.assertEqual(self.account.get_balance_at_date(), Decimal('1500.00'))

    def test_single_expense_transaction(self):
        """Verify that an expense transaction correctly reduces the balance."""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('200.00'),
            transaction_type="expense",
            category=self.expense_category
        )
        self.assertEqual(self.account.get_balance_at_date(), Decimal('800.00'))

    def test_multiple_transactions_same_date(self):
        """Test that multiple transactions on the same date are correctly calculated."""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('300.00'),
            transaction_type="income",
            category=self.income_category
        )
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('100.00'),
            transaction_type="expense",
            category=self.expense_category
        )
        self.assertEqual(self.account.get_balance_at_date(), Decimal('1200.00'))

    def test_future_transaction_not_included(self):
        """Ensure that future-dated transactions don't impact the current balance."""
        future_date = date.today() + timedelta(days=10)
        Transaction.objects.create(
            account=self.account,
            date=future_date,
            amount=Decimal('100.00'),
            transaction_type="expense",
            category=self.expense_category
        )
        self.assertEqual(self.account.get_balance_at_date(), Decimal('1000.00'))
        # Verify future balance
        self.assertEqual(
            self.account.get_balance_at_date(future_date), 
            Decimal('900.00')
        )

    def test_category_hierarchy(self):
        """Validate that category hierarchy is correctly maintained."""
        parent_category = TransactionCategory.objects.create(
            name="Household",
            transaction_type="expense"
        )
        sub_category = TransactionCategory.objects.create(
            name="Rent",
            transaction_type="expense",
            parent=parent_category
        )
        self.assertEqual(str(sub_category), "Household > Rent")

    def test_transaction_deletion(self):
        """Verify that deleting a transaction correctly updates the balance."""
        transaction = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('150.00'),
            transaction_type="expense",
            category=self.expense_category
        )
        self.assertEqual(self.account.get_balance_at_date(), Decimal('850.00'))
        
        transaction.delete()
        self.assertEqual(self.account.get_balance_at_date(), Decimal('1000.00'))

    def test_multiple_accounts_independence(self):
        """Test that transactions on different accounts don't affect each other."""
        second_account = Account.objects.create(
            name="Second Account",
            account_type="savings",
            initial_balance=Decimal('500.00'),
            institution="Test Bank"
        )

        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            amount=Decimal('100.00'),
            transaction_type="expense",
            category=self.expense_category
        )

        self.assertEqual(self.account.get_balance_at_date(), Decimal('900.00'))
        self.assertEqual(second_account.get_balance_at_date(), Decimal('500.00'))

    def test_transaction_category_validation(self):
        """Test that transactions must have matching category types."""
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                account=self.account,
                date=date.today(),
                amount=Decimal('100.00'),
                transaction_type="expense",
                category=self.income_category  # Mismatched category type
            )
            transaction.clean()

    def test_historical_balance(self):
        """Test balance calculation for past dates."""
        past_date = date.today() - timedelta(days=5)
        future_date = date.today() + timedelta(days=5)
        
        Transaction.objects.create(
            account=self.account,
            date=past_date,
            amount=Decimal('200.00'),
            transaction_type="income",
            category=self.income_category
        )
        Transaction.objects.create(
            account=self.account,
            date=future_date,
            amount=Decimal('300.00'),
            transaction_type="expense",
            category=self.expense_category
        )

        self.assertEqual(
            self.account.get_balance_at_date(past_date), 
            Decimal('1200.00')
        )
        self.assertEqual(
            self.account.get_balance_at_date(date.today()), 
            Decimal('1200.00')
        )
        self.assertEqual(
            self.account.get_balance_at_date(future_date), 
            Decimal('900.00')
        )