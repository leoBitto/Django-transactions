from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.models.base import *
from transactions.forms import *
from django.contrib import messages


class AccountView(LoginRequiredMixin, View):
    template_name = 'transactions/account.html'
    
    def get(self, request, *args, **kwargs):
        # Recupera tutti i conti bancari
        accounts = Account.objects.all()

        # Crea un dizionario con account come chiave e il saldo corrente come valore
        account_balances = {
            account: account.current_balance() for account in accounts
        }

        return render(request, self.template_name, {
            'account_balances': account_balances,
            'account_form': AccountForm(),
        })

    def post(self, request, *args, **kwargs):
        if 'create_account' in request.POST:
            form = AccountForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Account created successfully!')
                return redirect('transactions:account_view')

        # In caso di errore, ricarica i conti bancari e il form
        accounts = Account.objects.all()
        account_balances = {
            account: account.current_balance() for account in accounts
        }

        return render(request, self.template_name, {
            'account_balances': account_balances,
            'account_form': AccountForm(),
        })


class AccountDetailView(LoginRequiredMixin, View):
    template_name = 'transactions/account_detail.html'

    def get(self, request, account_id, *args, **kwargs):
        account = get_object_or_404(Account, id=account_id)
        form = AccountForm(instance=account) 
        transfer_form = TransferFundsForm(initial={'source_fund': account})

        # Calcola il bilancio giornaliero
        daily_balances = account.get_daily_balances()

        return render(request, self.template_name, {
            'account': account,
            'form': form,
            'transfer_form': transfer_form,
            'daily_balances': daily_balances
        })

    def post(self, request, account_id, *args, **kwargs):
        # Identifica il fondo attualmente selezionato come source_fund
        account = get_object_or_404(Account, id=account_id) 
        form = AccountForm(request.POST, instance=account) 
        
        if 'update_account' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, 'Account updated successfully!')
                return redirect('transactions:account_detail_view', account_id=account.id)

        elif 'delete_account' in request.POST:
            account.delete()
            messages.success(request, 'Account deleted successfully!')
            return redirect('transactions:account_view')

        elif 'transfer_funds' in request.POST:
            transfer_form = TransferFundsForm(request.POST)
            transfer_form.fields['source_fund'].initial = account

            if transfer_form.is_valid():
                amount = transfer_form.cleaned_data['amount']
                destination_fund = transfer_form.cleaned_data['destination_fund']
                commission = transfer_form.cleaned_data.get('commission', 0.00)

                # Effettua la logica del trasferimento
                account.calculate_current_balance()
                if account.balance >= amount + commission:
                    # Riduce il saldo dal conto di origine
                    account.balance -= (amount + commission)
                    account.save()

                    # Aggiunge il saldo al conto di destinazione
                    destination_fund.balance += amount
                    destination_fund.save()

                    messages.success(request, 'Funds transferred successfully!')
                    return redirect('transactions:account_detail_view', account_id=account.id)
                else:
                    messages.error(request, form.errors)

        # Ricarica i conti e i form in caso di errore
        return render(request, self.template_name, {
            'account': account,
            'form': form,
            'transfer_form': transfer_form,
        })


class IncomeView(LoginRequiredMixin, View):
    template_name = 'transactions/income.html'

    def get(self, request, *args, **kwargs):
        # Filtra solo le transazioni di tipo 'income'
        transactions = Transaction.objects.filter(transaction_type='income').order_by('-date', '-time')
        transaction_form = TransactionForm(
                initial={
                    'transaction_type': 'income', 
                    'category': TransactionCategory.objects.filter(transaction_type='income')
                })
        recurring_transaction_form = RecurringTransactionForm(
                initial={
                    'transaction_type': 'income', 
                    'category': TransactionCategory.objects.filter(transaction_type='income')
                })

        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': transaction_form,
            'recurring_transaction_form': recurring_transaction_form
        })

    def post(self, request, *args, **kwargs):
        if 'create_transaction' in request.POST:
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.instance.transaction_type = 'income'  # Imposta il tipo su 'income'
                form.save()
                messages.success(request, 'Income transaction created successfully!')
                return redirect('transactions:income_view')
            else:
                messages.error(request, 'Error creating income transaction.')

        elif 'create_recurring_transaction' in request.POST:
            recurring_form = RecurringTransactionForm(request.POST)
            if recurring_form.is_valid():
                start_date = recurring_form.cleaned_data['start_date']
                end_date = recurring_form.cleaned_data.get('end_date')
                frequency = recurring_form.cleaned_data['frequency']
                category = recurring_form.cleaned_data['category']
                amount = recurring_form.cleaned_data['amount']
                description = recurring_form.cleaned_data.get('description')
                account = recurring_form.cleaned_data['account']

                # Creazione delle transazioni ricorrenti
                current_date = start_date
                while current_date <= end_date:
                    # Crea una transazione per ogni data calcolata in base alla frequenza
                    if frequency == 'daily':
                        next_date = current_date + timedelta(days=1)
                    elif frequency == 'weekly':
                        next_date = current_date + timedelta(weeks=1)
                    elif frequency == 'monthly':
                        next_date = current_date + timedelta(weeks=4)
                    elif frequency == 'semi-annual':
                        next_date = current_date + timedelta(weeks=26)
                    elif frequency == 'annual':
                        next_date = current_date + timedelta(weeks=52)

                    # Crea la transazione
                    Transaction.objects.create(
                        date=next_date,
                        amount=amount,
                        description=description,
                        transaction_type='income',
                        category=category,
                        related_fund=account,
                    )

                    current_date = next_date  # Avanza alla prossima data

                messages.success(request, 'Recurring income transaction created successfully!')
                return redirect('transactions:income_view')
            else:
                messages.error(request, 'Error creating recurring income transaction.')

        # Ricarica le transazioni in caso di errore
        transactions = Transaction.objects.filter(transaction_type='income').order_by('-date', '-time')
        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': form,
            'recurring_transaction_form': recurring_form,
        })


class ExpenseView(LoginRequiredMixin, View):
    template_name = 'transactions/expense.html'

    def get(self, request, *args, **kwargs):
        # Filtra solo le transazioni di tipo 'expense'
        transactions = Transaction.objects.filter(transaction_type='expense').order_by('-date', '-time')
        transaction_form = TransactionForm(
                initial={
                    'transaction_type': 'expense', 
                    'category': TransactionCategory.objects.filter(transaction_type='expense')
                })
        recurring_transaction_form = RecurringTransactionForm(
                initial={
                    'transaction_type': 'expense', 
                    'category': TransactionCategory.objects.filter(transaction_type='expense')
                })

        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': transaction_form,
            'recurring_transaction_form': recurring_transaction_form
        })

    def post(self, request, *args, **kwargs):
        if 'create_transaction' in request.POST:
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.instance.transaction_type = 'expense'  # Imposta il tipo su 'expense'
                form.save()
                account = form.instance.related_fund
                account.calculate_current_balance()  # Calcola il saldo del fondo
                messages.success(request, 'Expense transaction created successfully!')
                return redirect('transactions:expense_view')
            else:
                messages.error(request, 'Error creating expense transaction.')

        elif 'create_recurring_transaction' in request.POST:
            recurring_form = RecurringTransactionForm(request.POST)
            if recurring_form.is_valid():
                start_date = recurring_form.cleaned_data['start_date']
                end_date = recurring_form.cleaned_data.get('end_date')
                frequency = recurring_form.cleaned_data['frequency']
                category = recurring_form.cleaned_data['category']
                amount = recurring_form.cleaned_data['amount']
                description = recurring_form.cleaned_data.get('description')
                account = recurring_form.cleaned_data['account']

                # Creazione delle transazioni ricorrenti
                current_date = start_date
                while current_date <= end_date:
                    # Crea una transazione per ogni data calcolata in base alla frequenza
                    if frequency == 'daily':
                        next_date = current_date + timedelta(days=1)
                    elif frequency == 'weekly':
                        next_date = current_date + timedelta(weeks=1)
                    elif frequency == 'monthly':
                        next_date = current_date + timedelta(weeks=4)
                    elif frequency == 'semi-annual':
                        next_date = current_date + timedelta(weeks=26)
                    elif frequency == 'annual':
                        next_date = current_date + timedelta(weeks=52)

                    # Crea la transazione
                    Transaction.objects.create(
                        date=next_date,
                        amount=amount,
                        description=description,
                        transaction_type='expense',
                        category=category,
                        related_fund=account,
                    )

                    current_date = next_date  # Avanza alla prossima data

                messages.success(request, 'Recurring expense transaction created successfully!')
                return redirect('transactions:expense_view')
            else:
                messages.error(request, 'Error creating recurring expense transaction.')

        # Ricarica le transazioni in caso di errore
        transactions = Transaction.objects.filter(transaction_type='expense').order_by('-date', '-time')
        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': form,
            'recurring_transaction_form': recurring_form,
        })


class TransactionDetailView(LoginRequiredMixin, View):
    template_name = 'transactions/transaction_detail.html'

    def get(self, request, transaction_id, *args, **kwargs):
        # Recupera la transazione
        transaction = get_object_or_404(Transaction, id=transaction_id)
        form = TransactionForm(instance=transaction)
        
        return render(request, self.template_name, {
            'transaction': transaction,
            'form': form,
        })

    def post(self, request, transaction_id, *args, **kwargs):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        form = TransactionForm(request.POST, instance=transaction)

        if 'update_transaction' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, 'Transaction updated successfully!')
                # Reindirizza a income o expense view in base al tipo di transazione
                return redirect('transactions:income_view' if transaction.transaction_type == 'income' else 'transactions:expense_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in field '{field}': {error}")

        elif 'delete_transaction' in request.POST:
            transaction_type = transaction.transaction_type  # Salva il tipo per il redirect
            transaction.delete()
            messages.success(request, 'Transaction deleted successfully!')
            return redirect('transactions:income_view' if transaction_type == 'income' else 'transactions:expense_view')

        return render(request, self.template_name, {
            'transaction': transaction,
            'form': form,
        })


class CategoryView(LoginRequiredMixin, View):
    template_name = 'transactions/category.html'

    def get(self, request, *args, **kwargs):
        expense_categories = TransactionCategory.objects.filter(transaction_type='expense')
        income_categories = TransactionCategory.objects.filter(transaction_type='income')
        return render(request, self.template_name, {
            'expense_categories': expense_categories,
            'income_categories':income_categories,
            'category_form': TransactionCategoryForm(),
        })

    def post(self, request, *args, **kwargs):
        if 'create_category' in request.POST:
            form = TransactionCategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category created successfully!')
                return redirect('transactions:category_view')

        # Ricarica le categorie in caso di errore
        expense_categories = TransactionCategory.objects.filter(transaction_type='expense')
        income_categories = TransactionCategory.objects.filter(transaction_type='income')
        return render(request, self.template_name, {
            'expense_categories': expense_categories,
            'income_categories':income_categories,
            'category_form': TransactionCategoryForm(),
        })


class CategoryDetailView(LoginRequiredMixin, View):
    template_name = 'transactions/category_detail.html'

    def get(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(TransactionCategory, id=category_id)
        form = TransactionCategoryForm(instance=category)
        
        return render(request, self.template_name, {
            'category': category,
            'form': form,
        })

    def post(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(TransactionCategory, id=category_id)
        form = TransactionCategoryForm(request.POST, instance=category)

        if 'update_category' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully!')
                return redirect('transactions:category_detail_view', category_id=category.id)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in field '{field}': {error}")

        elif 'delete_category' in request.POST:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
            return redirect('transactions:category_view')

        return render(request, self.template_name, {
            'category': category,
            'form': form,
        })
