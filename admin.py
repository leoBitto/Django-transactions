from django.contrib import admin
from .models.base import Account, Transaction, TransactionCategory

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'account_type', 'current_balance', 'created_at', 'is_active')
    search_fields = ('name', 'institution')
    list_filter = ('account_type', 'is_active', 'created_at')
    actions = ['mark_as_active', 'mark_as_inactive']

    @admin.action(description="Mark selected accounts as active")
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected accounts as inactive")
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def current_balance(self, obj):
        return f"{obj.current_balance()} €"
    current_balance.short_description = 'Current Balance'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'amount', 'transaction_type', 'category', 'description')
    list_filter = ('transaction_type', 'category', 'date', 'account')
    search_fields = ('description', 'category__name', 'account__name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'modified_at')

    def get_queryset(self, request):
        """Optimize queries by prefetching related fields"""
        return super().get_queryset(request).select_related('account', 'category')


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'transaction_type', 'parent', 'description')
    search_fields = ('name', 'parent__name')
    list_filter = ('transaction_type',)

    def get_queryset(self, request):
        """Get complete category hierarchy for better display"""
        return super().get_queryset(request).select_related('parent')