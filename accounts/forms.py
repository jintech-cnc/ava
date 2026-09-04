from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class ClientAdminForm(forms.ModelForm):
    class Meta:
        from orders.models import Client
        model = Client
        fields = ['nom', 'email', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'telephone': forms.TextInput(attrs={'class': 'input'}),
            'adresse': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }


class WarehouseAdminForm(forms.ModelForm):
    class Meta:
        from inventory.models import Warehouse
        model = Warehouse
        fields = ['nom', 'emplacement', 'responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'emplacement': forms.TextInput(attrs={'class': 'input'}),
            'responsable': forms.Select(attrs={'class': 'input'}),
        }


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        from inventory.models import Category
        model = Category
        fields = ['nom', 'description', 'image', 'is_hero']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'input'}),
            'is_hero': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }