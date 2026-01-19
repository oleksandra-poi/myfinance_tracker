from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('income/', views.add_income, name='add_income'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
    path('expense/', views.add_expense, name='add_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('register/', views.register, name='register'),
]
