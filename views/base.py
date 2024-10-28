from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models.base import *
from .forms import *
from django.contrib import messages


class AccountView(LoginRequiredMixin, View):
    template_name = 'transactions/account.html'
    
    def get(self, request, *args, **kwargs):
        bank_accounts = BankAccount.objects.all()
        cash_accounts = Cash.objects.all()
        transfer_form = TransferFundsForm()

        return render(request, self.template_name, {
            'bank_accounts': bank_accounts,
            'cash_accounts': cash_accounts,
            'transfer_form': transfer_form,
            'bank_account_form': BankAccountForm(),
            'cash_form': CashForm(),
        })

    def post(self, request, *args, **kwargs):
        if 'create_bank_account' in request.POST:
            form = BankAccountForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Bank account created successfully!')
                return redirect('transactions:account_view')

        elif 'create_cash_account' in request.POST:
            form = CashForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cash account created successfully!')
                return redirect('transactions:account_view')

        # Ricarica i conti e i form in caso di errore
        bank_accounts = BankAccount.objects.all()
        cash_accounts = Cash.objects.all()

        return render(request, self.template_name, {
            'bank_accounts': bank_accounts,
            'cash_accounts': cash_accounts,
            'transfer_form': transfer_form,
            'bank_account_form': BankAccountForm(),
            'cash_form': CashForm(),
        })


class AccountDetailView(LoginRequiredMixin, View):
    template_name = 'transactions/account_detail.html'

    def get(self, request, account_id, *args, **kwargs):
        # Identifica il fondo attualmente selezionato come source_fund
        account = get_object_or_404(BankAccount, id=account_id) if 'bank' in request.GET else get_object_or_404(Cash, id=account_id)
        form = BankAccountForm(instance=account) if isinstance(account, BankAccount) else CashForm(instance=account)
        transfer_form = TransferFundsForm(initial={'source_fund': account})

        # Disabilita il campo `source_fund` nel form per mostrare che è fisso
        transfer_form.fields['source_fund'].widget.attrs['readonly'] = True

        return render(request, self.template_name, {
            'account': account,
            'form': form,
            'transfer_form': transfer_form,
        })

    def post(self, request, account_id, *args, **kwargs):
        # Identifica il fondo attualmente selezionato come source_fund
        account = get_object_or_404(BankAccount, id=account_id) if 'bank' in request.GET else get_object_or_404(Cash, id=account_id)
        form = BankAccountForm(request.POST, instance=account) if isinstance(account, BankAccount) else CashForm(request.POST, instance=account)
        
        if 'update_account' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, 'Account updated successfully!')
                return redirect('transactions:account_detail', account_id=account.id)

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
                if account.balance >= amount + commission:
                    # Riduce il saldo dal conto di origine
                    account.balance -= (amount + commission)
                    account.save()

                    # Aggiunge il saldo al conto di destinazione
                    destination_fund.balance += amount
                    destination_fund.save()

                    messages.success(request, 'Funds transferred successfully!')
                    return redirect('transactions:account_detail', account_id=account.id)
                else:
                    messages.error(request, 'Insufficient funds for this transfer.')

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
        transactions = Transaction.objects.filter(transaction_type='income')
        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': TransactionForm(initial={'transaction_type': 'income'}),
            'recurring_transaction_form': RecurringTransactionForm(),
        })

    def post(self, request, *args, **kwargs):
        # Gestisce la creazione di una transazione normale o ricorrente
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
                # Logica per la creazione di transazioni ricorrenti
                messages.success(request, 'Recurring income transaction created successfully!')
                return redirect('transactions:income_view')
            else:
                messages.error(request, 'Error creating recurring income transaction.')

        # Ricarica le transazioni in caso di errore
        transactions = Transaction.objects.filter(transaction_type='income')
        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': form,
            'recurring_transaction_form': recurring_form,
        })


class ExpenseView(LoginRequiredMixin, View):
    template_name = 'transactions/expense.html'

    def get(self, request, *args, **kwargs):
        # Filtra solo le transazioni di tipo 'expense'
        transactions = Transaction.objects.filter(transaction_type='expense')
        return render(request, self.template_name, {
            'transactions': transactions,
            'transaction_form': TransactionForm(initial={'transaction_type': 'expense'}),
            'recurring_transaction_form': RecurringTransactionForm(),
        })

    def post(self, request, *args, **kwargs):
        # Gestisce la creazione di una transazione normale o ricorrente
        if 'create_transaction' in request.POST:
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.instance.transaction_type = 'expense'  # Imposta il tipo su 'expense'
                form.save()
                messages.success(request, 'Expense transaction created successfully!')
                return redirect('transactions:expense_view')
            else:
                messages.error(request, 'Error creating expense transaction.')

        elif 'create_recurring_transaction' in request.POST:
            recurring_form = RecurringTransactionForm(request.POST)
            if recurring_form.is_valid():
                # Logica per la creazione di transazioni ricorrenti
                messages.success(request, 'Recurring expense transaction created successfully!')
                return redirect('transactions:expense_view')
            else:
                messages.error(request, 'Error creating recurring expense transaction.')

        # Ricarica le transazioni in caso di errore
        transactions = Transaction.objects.filter(transaction_type='expense')
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
        categories = TransactionCategory.objects.all()
        return render(request, self.template_name, {
            'categories': categories,
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
        categories = TransactionCategory.objects.all()
        return render(request, self.template_name, {
            'categories': categories,
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
                return redirect('transactions:category_detail', category_id=category.id)
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
