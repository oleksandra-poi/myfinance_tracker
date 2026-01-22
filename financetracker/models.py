from django.db import models
from django.db.models import Sum
from datetime import date
from django.contrib.auth.models import User


class Category(models.Model):
    """Model for category"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Model for expense"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='expenses',
        verbose_name="Category")
    date = models.DateField(default=date.today, verbose_name="Date")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    @classmethod
    def get_total(cls, user):
        """Method to get total expense"""
        return cls.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

    @classmethod
    def get_by_month(cls, user, month, year):
        """Method to get expense by month and year"""
        return cls.objects.filter(user=user, date__month=month, date__year=year)

    def __str__(self):
        return f"{self.amount} - {self.category}"


class Income(models.Model):
    """Model for income"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=date.today, verbose_name="Date")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Income'
        verbose_name_plural = 'Income'

    @classmethod
    def get_total(cls, user):
        """Method to get total income"""
        return cls.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

    @classmethod
    def get_by_month(cls, user, month, year):
        """Method to get income by month and year"""
        return cls.objects.filter(user=user, date__month=month, date__year=year)

    def __str__(self):
        return f"{self.amount} - {self.category}"

