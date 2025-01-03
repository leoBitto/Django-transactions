from django.urls import path
from .views.base import *

app_name = 'transactions'

urlpatterns = [
    path('accounts/', AccountView.as_view(), name='account_view'),
    path('accounts/<int:account_id>/', AccountDetailView.as_view(), name='account_detail_view'),
    path('income/', IncomeView.as_view(), name='income_view'),
    path('expense/', ExpenseView.as_view(), name='expense_view'),
    path('transactions/<int:transaction_id>/', TransactionDetailView.as_view(), name='transaction_detail_view'),
    path('categories/', CategoryView.as_view(), name='category_view'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail_view'),
]
