from django.contrib import admin
from .models import Category, Expense, Income


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'description')
    list_filter = ('date', 'category')
    search_fields = ('description', 'category__name')
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'description')
    exclude = ('category',)
    list_filter = ('date',)
    search_fields = ('description',)