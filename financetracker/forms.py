from django import forms
from .models import Income, Expense, Category

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount which you spent..'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your expenses'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise forms.ValidationError("Amount must be positive")
        return amount

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount which you spent..'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your expenses'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise forms.ValidationError("Amount must be positive")
        return amount


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip().capitalize()
            if Category.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError('This category already exists')
        return name