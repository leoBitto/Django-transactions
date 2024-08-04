# Transactions App - Applicazione di Gestione Finanziaria

Benvenuti nell'applicazione Transactions, un'app Django per la gestione delle tue entrate, spese, asset e debiti.

## Caratteristiche Principali

1. **Registrazione delle Transazioni:** Puoi registrare entrate e spese tramite moduli dedicati. Le entrate includono categorie come "Salary", "Bonus", ecc., mentre le spese includono categorie come "Food", "Transport", ecc.

2. **Visualizzazione dei Dati Finanziari:** L'app offre una dashboard per visualizzare un riepilogo delle entrate e spese nel tempo. Vengono mostrati grafici a torta per le categorie di entrate e spese, nonché grafici a linee che tracciano le entrate e le spese nel corso del tempo.

3. **Controlli di Bilancio:** Prima di registrare una spesa, l'app esegue controlli per assicurarsi che il saldo del conto o del saldo cash non diventi negativo.

## Come Utilizzare l'App

### Requisiti

- Python 3.7 o versioni successive
- Django 3.1 o versioni successive
- Pacchetti Python aggiuntivi elencati in `requirements.txt`

### Installazione

1. Clona il repository dell'app:

   ```bash
   git clone https://github.com/leoBitto/transactions.git
Naviga nella directory del progetto:

cd transactions
Crea un ambiente virtuale (consigliato) e attivalo:

python3 -m venv venv
source venv/bin/activate
Installa i requisiti:

pip install -r requirements.txt
Applica le migrazioni:


python manage.py migrate
Avvia il server di sviluppo:


python manage.py runserver
Accedi all'app nel tuo browser all'indirizzo http://localhost:8000.

Uso dell'App
Dashboard: Accedi all'area protetta per visualizzare i tuoi dati finanziari, grafici e riepiloghi delle entrate e delle spese.

Registrazione delle Transazioni: Utilizza i moduli dedicati per registrare nuove entrate e spese. I controlli di bilancio assicurano che le spese non portino il conto o il saldo cash a un valore negativo.

Contributi
Se vuoi contribuire all'applicazione Transactions, sentiti libero di aprire un problema o inviare una richiesta pull nel repository GitHub: https://github.com/leoBitto/transactions

Licenza
L'applicazione è distribuita con licenza MIT. Consulta il file LICENSE per ulteriori dettagli.


# Documentazione dei Modelli

## Modello Bank Account

Il modello `BankAccount` rappresenta un'entità di un conto bancario.

- **Campi**:
  - `bank_name` (CharField): Il nome della banca associata al conto.
  - `balance` (DecimalField): Il saldo attuale del conto.
  - `start_date` (DateField): La data in cui è stato creato il conto.

- **Metodi**:
  - `transfer_money(target_account, amount, commissione)`: Trasferisce denaro da questo conto a un altro conto bancario.
  - `withdraw_money(amount, commissione)`: Preleva denaro dal conto.
  - `total_balance`: Calcola il saldo totale del conto fino alla data corrente.

## Modello Cash

Il modello `Cash` rappresenta un'entità contante.

- **Campi**:
  - `amount` (DecimalField): L'importo contante attuale.
  - `start_date` (DateField): La data in cui è stata creata l'entità contante.

- **Metodi**:
  - `total_amount`: Calcola l'importo totale del contante fino alla data corrente.

## Modello BalanceLog

Il modello `BalanceLog` registra le modifiche al saldo di un conto bancario.

- **Campi**:
  - `bank_account` (ForeignKey a BankAccount): Il conto bancario associato al registro del saldo.
  - `balance` (DecimalField): Il saldo al momento dell'entrata nel registro.
  - `timestamp` (DateTimeField): Il timestamp dell'entrata nel registro.

## Modello AmountLog

Il modello `AmountLog` registra le modifiche all'importo del contante.

- **Campi**:
  - `cash` (ForeignKey a Cash): L'entità contante associata al registro dell'importo.
  - `amount` (DecimalField): L'importo al momento dell'entrata nel registro.
  - `timestamp` (DateTimeField): Il timestamp dell'entrata nel registro.

## Modello Transaction

Il modello `Transaction` rappresenta una transazione finanziaria.

- **Campi**:
  - `date` (DateField): La data della transazione.
  - `amount` (DecimalField): L'importo della transazione.
  - `description` (CharField, opzionale): Una descrizione della transazione.
  - `bank_account` (ForeignKey a BankAccount, opzionale): Il conto bancario associato alla transazione.
  - `cash` (ForeignKey a Cash, opzionale): L'entità contante associata alla transazione.


## Modello Income

Il modello `Income` estende il modello `Transaction` per le transazioni di entrata.

- **Campi Aggiuntivi**:
  - `type` (CharField): Il tipo di entrata (ad esempio, stipendio, bonus).

## Modello Expenditure

Il modello `Expenditure` estende il modello `Transaction` per le transazioni di spesa.

- **Campi Aggiuntivi**:
  - `type` (CharField): Il tipo di spesa (ad esempio, cibo, bollette).

## Modello InvestmentAccount

Il modello `InvestmentAccount` rappresenta un conto d'investimento.

- **Campi**:
  - `account` (OneToOneField a BankAccount): Il conto bancario associato.
  - `portfolio` (ForeignKey a Portfolio, opzionale): Il portafoglio associato al conto d'investimento.






###################nuova documentazione vvvv
# Financial Management Application

## Introduzione

Questa applicazione è progettata per gestire i conti correnti e il contante, tenendo traccia delle transazioni finanziarie e mantenendo un registro dello storico dei saldi. L'app consente di registrare entrate, spese e altre transazioni in modo flessibile, supportando diversi tipi di fondi come conti bancari e denaro contante.

### Funzionalità Principali
- Creazione e gestione di conti bancari e contanti.
- Registrazione di transazioni finanziarie (entrate e spese).
- Tracciamento delle modifiche dei saldi nel tempo attraverso un sistema di log.
- Supporto per categorie di entrate e spese personalizzate.

## Modelli

### FundBase
`FundBase` è un modello astratto che fornisce una struttura comune per rappresentare un fondo finanziario, come un conto bancario o denaro contante. Include campi per il saldo (`balance`), la data di apertura (`start_date`) e la data di chiusura (`end_date`).

### BankAccount
`BankAccount` eredita da `FundBase` ed è utilizzato per rappresentare conti bancari specifici. Oltre ai campi base, include il tipo di conto (`account_type`), il nome dell'istituto bancario (`institution`) e il tasso d'interesse (`interest_rate`).

### Cash
`Cash` eredita da `FundBase` ed è utilizzato per rappresentare denaro contante. Include un campo aggiuntivo per la descrizione (`description`).

### FundLog
`FundLog` tiene traccia delle modifiche del saldo per qualsiasi tipo di fondo (`BankAccount` o `Cash`). Utilizza un `GenericForeignKey` per collegarsi dinamicamente al modello specifico di fondo.

### Transaction
`Transaction` rappresenta una transazione finanziaria generica. Può essere collegata a qualsiasi tipo di fondo (`BankAccount` o `Cash`) tramite una `GenericForeignKey`.

### Income
`Income` è un'estensione di `Transaction` per rappresentare entrate finanziarie. Ogni entrata è associata a una categoria (`IncomeCategory`).

### Expenditure
`Expenditure` è un'estensione di `Transaction` per rappresentare spese finanziarie. Ogni spesa è associata a una categoria (`ExpenseCategory`).

### Relazioni tra Modelli
I modelli `Income` e `Expenditure` ereditano da `Transaction` e sono collegati a categorie specifiche tramite relazioni `ForeignKey`. I modelli `BankAccount` e `Cash` sono collegati al log tramite `GenericForeignKey`.

### Esempi di Utilizzo
Di seguito un esempio di come creare e collegare un conto bancario e registrare una transazione:

```python
# Creare un nuovo conto bancario
bank_account = BankAccount.objects.create(
    balance=1000.00,
    start_date=date.today(),
    account_type='savings',
    institution='Bank XYZ',
    interest_rate=1.5
)

# Creare una nuova transazione di entrata
income_category = IncomeCategory.objects.create(name='Salary', description='Monthly salary')
income = Income.objects.create(
    date=date.today(),
    amount=500.00,
    related_fund=ContentType.objects.get_for_model(bank_account),
    object_id=bank_account.id,
    type=income_category
)
```

## Signal e Logging

### Signal `log_fund_change`
Il signal `log_fund_change` è collegato ai modelli `BankAccount` e `Cash`. Viene attivato ogni volta che un fondo viene aggiornato (non creato) e crea un nuovo record in `FundLog` per registrare il cambiamento del saldo.

### Gestione del Logging
Il modello `FundLog` utilizza un `GenericForeignKey` per collegarsi dinamicamente a qualsiasi tipo di fondo (`BankAccount` o `Cash`). Questo sistema di logging consente di tracciare l'andamento del saldo nel tempo, offrendo uno storico dettagliato delle operazioni sui fondi.

























