from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from django.contrib import messages
from datetime import date
from datetime import datetime
from decimal import Decimal
import logging
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import JsonResponse
from calendar import monthrange


@login_required
def index(request):
    today = date.today()
    future_expenses = Expenditure.objects.filter(date__gt=today)
    
    for expense in future_expenses:
        # Esempio: Se la data è entro una settimana dalla data odierna, considera la spesa urgente
        if (expense.date - today).days <= 7:
            expense.is_urgent = True

    # Gestione dei BankAccount
    try:
        bank_accounts = BankAccount.objects.all()
    except Cash.DoesNotExist:
        bank_accounts = []

    # Gestione dei Cash
    try:
        cash_amounts = Cash.objects.all()
    except Cash.DoesNotExist:
        cash_amounts = []

    # Gestione dei Portfolio
    try:
        portfolios = Portfolio.objects.all()
    except Portfolio.DoesNotExist:
        portfolios = []

    # Calcola il totale dei risparmi
    total_savings = sum([account.balance for account in bank_accounts]) + sum([cash.amount for cash in cash_amounts]) + sum([portfolio.total_value for portfolio in portfolios])

    # aggiungi i form
    add_bank_form = AddBankForm()
    add_cash_form = AddCashAmountForm()


    context = {
        'future_expenses':future_expenses,
        'cash_amounts':cash_amounts,
        'bank_accounts': bank_accounts,
        'portfolios' : portfolios,
        'total_savings': total_savings,
        'add_bank_form': add_bank_form,
        'add_cash_form': add_cash_form,

    }
    
    return render(request, 'transactions/overview.html', context)

# Create your views here.
@login_required
def financial_summary(request):
    if request.method == 'POST':
        # Se il form è stato inviato via POST, accedi ai dati inviati dal form
        start_date = request.POST.get('startDate')  # Assumi che l'input del form abbia il nome 'startDate'
        end_date = request.POST.get('endDate')  # Assumi che l'input del form abbia il nome 'endDate'
    else:
        # Se la richiesta non è una POST, usa delle date di default 
        start_date = '2023-01-01'
        end_date = '2023-12-31'

    # Filtra le entrate e le spese utilizzando le date specificate o quelle di default
    incomes = Income.objects.filter(date__range=[start_date, end_date]).order_by('-date', 'amount')
    expenditures = Expenditure.objects.filter(date__range=[start_date, end_date]).order_by('-date', 'amount')

    # Converti i risultati della query in un DataFrame
    incomes_data = list(incomes.values('date', 'amount', 'type'))
    incomes_df = pd.DataFrame(incomes_data)

    # Esegui lo stesso processo per le uscite
    expenditures_data = list(expenditures.values('date', 'amount', 'type'))
    expenditures_df = pd.DataFrame(expenditures_data)

    #definisci dei colori per le categorie di spesa:
    income_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  
    expense_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


    # Verifica se ci sono dati validi per i grafici
    if not incomes_df.empty:
        # Crea e visualizza il grafico a torta per le categorie di entrate
        fig_pie_income = px.pie(incomes_df, names='type', values='amount', title='Income Categories',color='type',
                        color_discrete_sequence=income_colors)
        fig_pie_income.update_layout(
            legend=dict(x=0, y=0, traceorder='normal', font=dict(family='sans-serif', size=12, color='black'))
        )

        html_pie_income = pio.to_html(fig_pie_income)
    else:
        html_pie_income = "No income data available"

    if not expenditures_df.empty:
        # Crea e visualizza il grafico a torta per le categorie di uscite
        fig_pie_expenditure = px.pie(expenditures_df, names='type', values='amount', title='Expenses Categories',color='type',
                        color_discrete_sequence=expense_colors)
        fig_pie_expenditure.update_layout(
            legend=dict(x=0, y=0, traceorder='normal', font=dict(family='sans-serif', size=12, color='black'))
        )
        html_pie_expenditure = pio.to_html(fig_pie_expenditure)
    else:
        html_pie_expenditure = "No expenditure data available"

    if not incomes_df.empty:
        # Calcola le somme totali delle entrate per ogni giorno
        total_incomes_per_day = incomes_df.groupby('date')['amount'].sum().reset_index()

        # Crea e visualizza il grafico a linee per le entrate nel tempo
        fig_line_income = px.line(incomes_df, x='date', y='amount', color='type', title='Income Over Time', color_discrete_sequence=income_colors)
        # Aggiungi la linea delle entrate totali
        fig_line_income.add_trace(go.Scatter(x=total_incomes_per_day['date'], y=total_incomes_per_day['amount'],
                                     mode='lines+markers', name='Total Income'))
        # Aggiorna il layout per spostare la legenda all'interno del grafico
        fig_line_income.update_layout(
            legend=dict(x=0, y=-1, traceorder='normal', font=dict(family='sans-serif', size=12, color='black'))
        )

        html_line_income = pio.to_html(fig_line_income)
    else:
        html_line_income = "No income data available"

    if not expenditures_df.empty:
        # Calcola le somme totali delle entrate per ogni giorno
        total_expenses_per_day = expenditures_df.groupby('date')['amount'].sum().reset_index()

        # Crea e visualizza il grafico a linee per le entrate nel tempo
        fig_line_expenditure = px.line(expenditures_df, x='date', y='amount', color='type', title='Expenses Over Time', color_discrete_sequence=expense_colors)
        # Aggiungi la linea delle entrate totali
        fig_line_expenditure.add_trace(go.Scatter(x=total_expenses_per_day['date'], y=total_expenses_per_day['amount'],
                                     mode='lines+markers', name='Total Expenses'))
        # Aggiorna il layout per spostare la legenda all'interno del grafico
        fig_line_expenditure.update_layout(
            legend=dict(x=0, y=-1, traceorder='normal', font=dict(family='sans-serif', size=12, color='black'))
        )

        html_line_expenditure = pio.to_html(fig_line_expenditure)
    else:
        html_line_expenditure = "No expenditure data available"


     # Ottieni gli account bancari e l'entità Cash dal database
    bank_accounts = BankAccount.objects.all()
    cash_entity = Cash.objects.first() # Assumendo che ci sia solo un oggetto Cash nel database

    income_choices = Income.Choices
    expenditure_choices = Expenditure.Choices

    context = {

        'bank_accounts': bank_accounts, 
        'cash_entity': cash_entity,
        'income_choices': income_choices,
        'expenditure_choices': expenditure_choices,

        'incomes': incomes,
        'expenditures': expenditures,
        'fig_pie_income':html_pie_income,
        'fig_pie_expenditure':html_pie_expenditure,
        'fig_line_income':html_line_income,
        'fig_line_expenditure':html_line_expenditure,
        'income_form': IncomeForm(),
        'expenditure_form': ExpenditureForm(),
        'today': date.today().strftime('%Y-%m-%d'),
        'now': datetime.now().strftime('%H:%M'),
    }
        

    # Restituisci la risposta rendendo il template 'transactions/Transactions.html'
    return render(request, 'transactions/transactions.html', context)


@login_required
def income_registration(request):
    if request.method == 'POST':
        income_form = IncomeForm(request.POST)

        if income_form.is_valid():
            # Gestione delle entrate
            income = income_form.save(commit=False)  # Non salvare subito nel database

            # Controlla se esiste un guadagno simile nello stesso giorno e dello stesso tipo
            existing_income = Income.objects.filter(date=income.date, type=income.type).first()


            if existing_income:
                # Aggiorna l'importo del guadagno esistente
                existing_income.amount += Decimal(str(income.amount))
                existing_income.save()
            else:
                # Crea una nuova voce nel database per il guadagno
                income.save()

            # Aggiorna il saldo del conto bancario associato
            if income.bank_account:
                bank_account = BankAccount.objects.get(pk=income.bank_account.pk)
                bank_account.balance += Decimal(str(income.amount))
                bank_account.save()

            # Aggiorna l'entità cash se presente
            if income.cash:
                cash = Cash.objects.get(pk=income.cash.pk)
                cash.amount += Decimal(str(income.amount))
                cash.save()

            messages.success(request, 'Income saved successfully!')

            return redirect('transactions:financial_summary')
        else:
            for field, errors in income_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    return redirect('transactions:financial_summary')


@login_required
def expense_registration(request):
    if request.method == 'POST':
        expenditure_form = ExpenditureForm(request.POST)


        if expenditure_form.is_valid():
            # Gestione delle spese
            expenditure = expenditure_form.save(commit=False)  # Non salvare subito nel database

            # Controlla se la spesa porta il saldo del conto o del contante a un valore negativo
            if expenditure.bank_account:
                bank_account = BankAccount.objects.get(pk=expenditure.bank_account.pk)
                if bank_account.balance - expenditure.amount < 0:
                    messages.error(request, "La spesa supera il saldo disponibile.")
                    return redirect('transactions:financial_summary')

            if expenditure.cash:
                cash = Cash.objects.get(pk=expenditure.cash.pk)
                if cash.amount - Decimal(str(expenditure.amount)) < 0:
                    messages.error(request, "La spesa supera il saldo cash disponibile.")
                    return redirect('transactions:financial_summary')


            # Controlla se esiste una spesa simile nello stesso giorno e dello stesso tipo
            existing_expenditure = Expenditure.objects.filter(date=expenditure.date, type=expenditure.type).first()

            if existing_expenditure:
                # Aggiorna l'importo della spesa esistente
                existing_expenditure.amount += Decimal(str(expenditure.amount))
                existing_expenditure.save()
            else:
                # Crea una nuova voce nel database per la spesa
                expenditure.save()

            # Aggiorna il saldo del conto bancario associato
            if expenditure.bank_account:
                bank_account = BankAccount.objects.get(pk=expenditure.bank_account.pk)
                bank_account.balance -= Decimal(str(expenditure.amount))
                bank_account.save()

            # Aggiorna l'entità cash se presente
            if expenditure.cash:
                cash = Cash.objects.get(pk=expenditure.cash.pk)
                cash.amount -= Decimal(str(expenditure.amount))
                cash.save()

            messages.success(request, 'Expenditure saved successfully!')

            return redirect('transactions:financial_summary')
        else:
            for field, errors in expenditure_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    return redirect('transactions:financial_summary')


@login_required
def bank_detail(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    bank_accounts = BankAccount.objects.exclude(pk=pk)
    cash_amounts = Cash.objects.all()
    
    if request.method == 'POST':
        print(request)
        if 'transfer_button' in request.POST:
            target_account_name = request.POST.get('target_account')
            amount = Decimal(request.POST.get('amount'))
            commission = Decimal(request.POST.get('commission'))
            
            # crea una expenditure per la commissione
            Expenditure.objects.create(
                type = 'Other',
                date=date.today(),
                amount=commission,
                bank_account=bank_account,
                description='commissione',
                )

            try:
                target_account = BankAccount.objects.get(name=target_account_name)
            except BankAccount.DoesNotExist:
                raise Http404("L'account bancario di destinazione non esiste.")

            if bank_account.transfer_money(target_account, amount, commission):
                messages.success(request, 'Il trasferimento è avvenuto con successo.')
            else:
                messages.error(request, 'Il trasferimento non è riuscito.')

        elif 'retire_button' in request.POST:
            target_account_id = request.POST.get('target_account')
            
            retire_amount = Decimal(request.POST.get('retire_amount'))
            retire_commission = Decimal(request.POST.get('retire_commission'))
            # crea una expenditure per la commissione
            Expenditure.objects.create(
                type = 'Other',
                date=date.today(),
                amount=retire_commission,
                bank_account=bank_account,
                description='commissione',
                )
            
            try:
                target_account = Cash.objects.get(pk=target_account_id)
            except Cash.DoesNotExist:
                raise Http404("L'ammontare di denaro di destinazione non esiste.")


            if bank_account.withdraw_money(target_account, retire_amount, retire_commission):
                messages.success(request, 'Il ritiro è avvenuto con successo.')
            else:
                messages.error(request, 'Il ritiro non è riuscito.')

        return redirect('transactions:bank_detail', pk=pk)
    

    balance_logs = BalanceLog.objects.filter(bank_account=bank_account)

    df = pd.DataFrame(list(balance_logs.values()))
   
    # Verifica se il DataFrame df è vuoto
    if not df.empty:
        fig = px.line(df, x='timestamp', y='balance', title='Balance Over Time')
        fig.update_xaxes(title_text='Timestamp')
        fig.update_yaxes(title_text='Balance')

        # Genera il grafico Plotly e il codice HTML solo se il DataFrame non è vuoto
        html_fig = pio.to_html(fig)
    else:
        # DataFrame vuoto, imposta html_fig a una stringa vuota o un messaggio di avviso
        html_fig = "<p class='m-4'>No record to show</p>"


    context = {
        'bank_account': bank_account, 
        'bank_accounts': bank_accounts,
        'cash_amounts': cash_amounts,
        'html_fig':html_fig,
    }

    return render(request, 'transactions/bank_detail.html', context)

@login_required
def add_bank(request):
    if request.method == 'POST':
        bank_form = AddBankForm(request.POST)
        if bank_form.is_valid():
            name = bank_form.cleaned_data['name']
            balance = bank_form.cleaned_data['balance']
            start_date = bank_form.cleaned_data['start_date']

            BankAccount.objects.create(
                name = name,
                balance = balance,
                start_date = start_date,
            )


    return redirect("transactions:index")

@login_required
def add_cash_amount(request):
    if request.method == 'POST':
        cash_form = AddCashAmountForm(request.POST)
        if cash_form.is_valid():
            
            amount = cash_form.cleaned_data['amount']
            start_date = cash_form.cleaned_data['start_date']

            Cash.objects.create(
                amount = amount,
                start_date = start_date,
            )


    return redirect("transactions:index")

@login_required
def cash_detail(request, pk):
    cash_account = get_object_or_404(Cash, pk=pk)

    amount_logs = AmountLog.objects.all()

    deposit_form = DepositForm()  # Aggiungi questa linea per istanziare il form

    if request.method == 'POST':
        deposit_form = DepositForm(request.POST)  # Ottieni i dati dal form

        if deposit_form.is_valid():
            amount = deposit_form.cleaned_data['amount']
            bank_account = deposit_form.cleaned_data['bank_account']

            # Crea una transazione di deposito nel conto bancario
            Transaction.objects.create(
                date=date.today(),
                amount=amount,
                description='Deposito cash',
                bank_account=bank_account
            )

            # Aggiorna l'entità Cash
            cash_account.amount -= amount
            cash_account.save()

            # Aggiorna il saldo del conto bancario
            bank_account.balance += amount
            bank_account.save()

            messages.success(request, 'Il deposito è avvenuto con successo.')
            return redirect('transactions:cash_detail', pk=pk)


    df = pd.DataFrame(list(amount_logs.values()))

    # Verifica se il DataFrame df è vuoto
    if not df.empty:
        fig = px.line(df, x='timestamp', y='amount', title='Amount Over Time')
        fig.update_xaxes(title_text='Timestamp')
        fig.update_yaxes(title_text='Amount')

        # Genera il grafico Plotly e il codice HTML solo se il DataFrame non è vuoto
        html_fig = pio.to_html(fig)
    else:
        # DataFrame vuoto, imposta html_fig a una stringa vuota o un messaggio di avviso
        html_fig = "<p class='m-4'>No record to show</p>"

    context = {
        'cash_account': cash_account,
        'html_fig':html_fig,
        'deposit_form': deposit_form,  # Passa il form al contesto del template

        }

    return render(request, 'transactions/cash_detail.html', context)

@login_required
def create_recurring_transaction(request):
    # Ottieni gli account bancari e l'entità Cash dal database
    bank_accounts = BankAccount.objects.all()
    cash_entity = Cash.objects.all()[0]  # Assumendo che ci sia solo un oggetto Cash nel database


    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST)
        if form.is_valid():
            # Eseguire il salvataggio manuale dei dati del form
            amount = form.cleaned_data['amount']
            frequency = form.cleaned_data['frequency']
            transaction_type = form.cleaned_data['type']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            description = form.cleaned_data['description']
            payment_method = form.cleaned_data['payment_method']
            income_type = form.cleaned_data['income_type']
            expenditure_type = form.cleaned_data['expenditure_type']
            
            if payment_method == 'cash':
                selected_cash_entity = cash_entity
                selected_bank_account = None
            else:
                selected_bank_account = BankAccount.objects.get(pk=payment_method)
                selected_cash_entity = None

            # Verifica se la data di fine è stata fornita
            if end_date and end_date >= date.today():
                _, days_in_start_month = monthrange(start_date.year, start_date.month)
                delta = end_date - start_date
                total_days = delta.days

                if frequency == 'daily':
                    increment = timedelta(days=1)
                elif frequency == 'weekly':
                    increment = timedelta(weeks=1)
                elif frequency == 'monthly':
                    increment = timedelta(days=days_in_start_month)
                elif frequency == 'annual':
                    _, days_in_year = monthrange(start_date.year, 12)
                    increment = timedelta(days=days_in_year)
                else:
                    increment = None
                    total_days = 0

                for i in range(total_days):
                    new_date = start_date + i * increment
                    _, days_in_month = monthrange(new_date.year, new_date.month)

                    if new_date.day > days_in_month:
                        new_date = new_date.replace(day=days_in_month)

                    if transaction_type == 'income':
                        new_transaction = Income(
                            date=new_date,
                            amount=amount,
                            description=description,
                            bank_account=selected_bank_account,
                            cash=selected_cash_entity,
                            type=income_type,
                        )
                    else:
                        new_transaction = Expenditure(
                            date=new_date,
                            amount=amount,
                            description=description,
                            bank_account=selected_bank_account,
                            cash=selected_cash_entity,
                            type=expenditure_type,
                        )

                    new_transaction.save()

            elif not end_date:
                # Se la data di fine non è stata fornita, crea una sola transazione
                if transaction_type == 'income':
                    new_transaction = Income(
                        date=start_date,
                        amount=amount,
                        description=description,
                        bank_account=bank_accounts.first(),  # Cambia con l'account bancario corretto
                        cash=cash_entity,
                        type=expenditure_type,
                    )
                else:
                    new_transaction = Expenditure(
                        date=start_date,
                        amount=amount,
                        description=description,
                        bank_account=bank_accounts.first(),  # Cambia con l'account bancario corretto
                        cash=cash_entity,
                        type=expenditure_type,
                    )

                new_transaction.save()

            return redirect('transactions:financial_summary')
    else:
        form = RecurringTransactionForm()


    return redirect('transactions:financial_summary')

@login_required
def create_portfolio(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')  # Assicurati che il form abbia un campo 'start_date'
        balance = request.POST.get('balance')
                
        
        # Crea un nuovo portfolio
        portfolio = Portfolio.objects.create(
            name=name, 
            start_date=start_date,
            balance = balance
            )

        # Reindirizza alla pagina di dettaglio del nuovo portfolio
        return redirect('transactions:portfolio_details', pk=portfolio.pk)

    # Se il metodo non è POST, visualizza il form per la creazione
    return render(request, 'transactions/create_portfolio.html')

@login_required
def eliminate_portfolio(request, pk):
                    
    # elimina portfolio
    Portfolio.objects.filter(pk=pk).delete()

    # Reindirizza alla pagina iniziale
    return redirect('transactions:index')

@login_required
def portfolio_details(request, pk):
    '''
    Gives an overview of the portfolio
    '''
    form_stocks = TransactionStockForm()
    form_cash = ManageCashForm()
    portfolio = Portfolio.objects.get(pk=pk)
    
    context={
        "portfolio":portfolio,
        'companies': Company.objects.all(),  # Aggiungi le aziende disponibili
        'form_stocks':form_stocks,
        'form_cash':form_cash,
    }

    return render(request, 'transactions/portfolio.html', context)

@login_required
def manage_stock(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)

    if request.method == 'POST':
        form = TransactionStockForm(request.POST)

        if form.is_valid():
            company_name = form.cleaned_data['company']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            commission = form.cleaned_data['commission']
            date = form.cleaned_data['transaction_date']
            transaction_type = form.cleaned_data['transaction_type']

            if transaction_type == 'BUY':
                company = get_object_or_404(Company, name=company_name)
                total_purchase_cost = (quantity * price) + commission

                if total_purchase_cost <= portfolio.cash_balance:
                    try:
                        stock = StockInPortfolio.objects.get(related_portfolio=portfolio, company=company)
                    except StockInPortfolio.DoesNotExist:
                        stock = None

                    if stock:
                        stock.quantity += quantity
                        stock.price = (stock.price + price) / 2
                        stock.save()
                    else:
                        stock = StockInPortfolio.objects.create(
                            related_portfolio=portfolio,
                            company=company,
                            quantity=quantity,
                            price=price,
                        )

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type='BUY',
                        quantity=quantity,
                        price=price,
                        commission=commission,
                        transaction_date=date
                    )

                    # Aggiornamento dei valori del portafoglio
                    portfolio.cash_balance -= total_purchase_cost
                    tot_stock_val = 0
                    for stock in StockInPortfolio.objects.filter(related_portfolio=portfolio):
                        tot_stock_val = stock.quantity * stock.price
                    portfolio.stock_value = tot_stock_val
                    portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
                    portfolio.save()

                else:
                    messages.error(request, 'Fondi insufficienti per acquistare queste azioni.')
            
            else: # transaction_type == 'SELL'
                
                company = get_object_or_404(StockInPortfolio, company__name=company_name, related_portfolio=portfolio)
                
                if quantity <= company.quantity:
                    company.quantity -= quantity
                    company.save()

                    StockTransaction.objects.create(
                        stock=company,
                        transaction_type='SELL',
                        quantity=quantity,
                        price=price,
                        commission=commission,
                        transaction_date=date
                    )

                    # Aggiornamento dei valori del portafoglio
                    portfolio.cash_balance += (quantity * price - commission)
                    tot_stock_val = 0
                    for stock in StockInPortfolio.objects.filter(related_portfolio=portfolio):
                        tot_stock_val = stock.quantity * stock.price
                    portfolio.stock_value = tot_stock_val
                    portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
                    portfolio.save()

                    # Se la quantità rimanente è zero, elimina l'oggetto StockInPortfolio
                    if company.quantity == 0:
                       company.delete()

                else:
                    messages.error(request, 'La quantità venduta supera la quantità disponibile.')


    else:
        form = TransactionStockForm()

    context = {
        'portfolio': portfolio,
        'companies': Company.objects.all(),
        'form_stocks': form,
        'form_cash': ManageCashForm(),
    }

    return render(request, 'transactions/portfolio.html', context)

@login_required
def manage_cash(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)

    if request.method == 'POST':
        form = ManageCashForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction_type = form.cleaned_data['transaction_type']
            commission = form.cleaned_data['commission']

            if transaction_type == 'DEPOSIT':
                portfolio.cash_balance += (amount - commission)
                portfolio.total_investment += (amount - commission)
            elif transaction_type == 'WITHDRAW':
                if (amount + commission) <= portfolio.cash_balance:
                    portfolio.cash_balance -= (amount + commission)
                    portfolio.total_investment -= (amount + commission)  # Aggiornamento dell'investimento iniziale
                else:
                    messages.error(request, 'La quantità richiesta supera la quantità disponibile.')

            portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
            portfolio.save()

    else:
        form = ManageCashForm()

    context = {
        'portfolio': portfolio,
        'companies': Company.objects.all(),
        'form_stocks': TransactionStockForm(),
        'form_cash': form,
    }

    return render(request, 'transactions/portfolio.html', context)


