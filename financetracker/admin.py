from django.contrib import admin
from .models import Category, Expense, Income


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'category', 'amount', 'description']
    list_filter = ['date', 'user', 'category']
    search_fields = ['description', 'category__name', 'user__username']
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'amount', 'description']
    exclude = ['category']
    list_filter = ['date', 'user']
    search_fields = ['description', 'user__username']