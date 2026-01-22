import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Expense, Income
from .forms import ExpenseForm, IncomeForm
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Home page with balance overview"""
    # Calculate total income and expenses
    total_income = Income.get_total(request.user)
    total_expenses = Expense.get_total(request.user)

    balance = total_income - total_expenses

    context = {
        'balance': balance,
    }
    return render(request, 'financetracker/home.html', context)


@login_required
def transactions_list(request):
    """Simple list of transactions with day, week, and month filtering."""
    # Get current filter type and today's date
    filter_type = request.GET.get('filter', 'all')
    now = timezone.now().date()

    # Initial querysets with default sorting
    expenses = Expense.objects.filter(user=request.user).order_by('-date', '-id')
    income = Income.objects.filter(user=request.user).order_by('-date', '-id')

    # Apply date filtering logic
    if filter_type == 'day':
        # Show only today's records
        expenses = expenses.filter(date=now)
        income = income.filter(date=now)

    elif filter_type == 'week':
        # Calculate strict week bounds within current month
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        first_day_of_month = now.replace(day=1)

        # Ensure we don't show transactions from the previous month
        actual_start = max(start_of_week, first_day_of_month)

        expenses = expenses.filter(date__range=[actual_start, end_of_week])
        income = income.filter(date__gte=actual_start, date__month=now.month)

    elif filter_type == 'month':
        # Filter by current month and year
        expenses = expenses.filter(date__month=now.month, date__year=now.year)
        income = income.filter(date__month=now.month, date__year=now.year)

    return render(request, 'financetracker/transactions.html', {
        'expenses': expenses,
        'income': income,
        'current_filter': filter_type
    })


@login_required
def add_expense(request):
    """Page for adding expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Link to current user
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'financetracker/add_expense.html', {'form': form})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('transactions_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'financetracker/add_expense.html', {'form': form})


@login_required
def delete_expense(request, pk):
    # Security check: only delete if it's the user's record
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('transactions_list')


@login_required
def add_income(request):
    """Page for adding income"""
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('home')
    else:
        form = IncomeForm()
    return render(request, 'financetracker/add_income.html', {'form': form})


@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('transactions_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'financetracker/add_income.html', {'form': form})


@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect('transactions_list')


@login_required
def statistics_view(request):
    """Statistics page with charts and analysis"""
    # Get current month and year
    current_date = datetime.now()
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Filter by selected month (default: current month)
    selected_month = request.GET.get('month', current_month)
    selected_year = request.GET.get('year', current_year)

    try:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    except (ValueError, TypeError):
        selected_month = current_month
        selected_year = current_year

    # Base queryset filtered by user
    user_expenses = Expense.get_by_month(request.user, selected_month, selected_year)
    user_incomes = Income.get_by_month(request.user, selected_month, selected_year)

    # Calculate expenses by category
    expenses_by_category = user_expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')

    # Calculate totals
    total_month_expenses = user_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_month_income = user_incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    monthly_balance = total_month_income - total_month_expenses

    # Calculate average daily expense
    # --- 1. ACCURATE DAY CALCULATION START ---
    if selected_month == current_month and selected_year == current_year:
        # For the current month, we divide by the current day (e.g., Jan 7th -> divide by 7)
        days_to_count = current_date.day
    else:
        # For past/future months, we get the exact number of days (28, 30, or 31)
        _, days_in_month = calendar.monthrange(selected_year, selected_month)
        days_to_count = days_in_month

    avg_daily = total_month_expenses / days_to_count if days_to_count > 0 else 0

    # Prepare data for Chart.js
    category_labels = []
    category_amounts = []

    for item in expenses_by_category:
        name = item['category__name'] if item['category__name'] else "Other"
        category_labels.append(name)
        category_amounts.append(float(item['total']))
    # --- CHART PROTECTION END ---

    context = {
        'total_month_expenses': total_month_expenses,
        'total_month_income': total_month_income,
        'monthly_balance': monthly_balance,
        'avg_daily': avg_daily,
        'category_labels': category_labels,
        'category_amounts': category_amounts,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }

    return render(request, 'financetracker/statistics.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'financetracker/register.html', {'form': form})
