from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense, Income, Category
from django.utils import timezone

class AuthAndRegistrationTests(TestCase):
    """Tests for user registration and access security"""

    def setUp(self):
        """Initialize client and test user for auth checks"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_anonymous_access_redirect(self):
        """Verify that unauthorized users are redirected from the home page"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_registration_success(self):
        """Verify user registration with correct Django field names"""
        data = {
            'username': 'test_new_user',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        response = self.client.post(reverse('register'), data)

        # Now it should successfully validate and redirect (302)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='test_new_user').exists())

class ExpenseCRUDTests(TestCase):
    """Tests for creating, updating, and deleting expenses"""

    def setUp(self):
        """Setup user, category and login for expense operations"""
        self.client = Client()
        self.user = User.objects.create_user(username='exp_user', password='password123')
        self.category = Category.objects.create(name="Food")
        self.client.login(username='exp_user', password='password123')

    def test_add_expense(self):
        """Verify adding a new expense record"""
        data = {
            'amount': 50,
            'category': self.category.id,
            'description': 'Coffee',
            'date': timezone.now().date()
        }
        response = self.client.post(reverse('add_expense'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 1)

    def test_edit_expense(self):
        """Verify updating an existing expense record"""
        expense = Expense.objects.create(user=self.user, amount=10, category=self.category, date=timezone.now().date())
        data = {
            'amount': 25,
            'category': self.category.id,
            'description': 'Updated',
            'date': timezone.now().date()
        }
        response = self.client.post(reverse('edit_expense', args=[expense.id]), data)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, 25)

    def test_delete_expense(self):
        """Verify deleting an expense record"""
        expense = Expense.objects.create(user=self.user, amount=10, category=self.category, date=timezone.now().date())
        response = self.client.post(reverse('delete_expense', args=[expense.id]))
        self.assertEqual(Expense.objects.count(), 0)

class IncomeCRUDTests(TestCase):
    """Tests for creating, updating, and deleting income records"""

    def setUp(self):
        """Setup user and login for income operations"""
        self.client = Client()
        self.user = User.objects.create_user(username='inc_user', password='password123')
        self.client.login(username='inc_user', password='password123')

    def test_add_income(self):
        """Verify adding a new income record"""
        data = {'amount': 500, 'description': 'Bonus', 'date': timezone.now().date()}
        response = self.client.post(reverse('add_income'), data)
        self.assertEqual(Income.objects.filter(user=self.user).count(), 1)

    def test_delete_income(self):
        """Verify deleting an income record"""
        income = Income.objects.create(user=self.user, amount=100, description='Gift', date=timezone.now().date())
        self.client.post(reverse('delete_income', args=[income.id]))
        self.assertEqual(Income.objects.count(), 0)

class FinanceLogicTests(TestCase):
    """Tests for complex calculations and date filtering"""