from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Product, StockMovement, Category, Warehouse


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'reference', 'nom', 'description', 'categorie',
            'unite', 'prix_unitaire', 'seuil_alerte', 'actif',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'input'}),
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'categorie': forms.Select(attrs={'class': 'input'}),
            'unite': forms.TextInput(attrs={'class': 'input'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'input'}),
            'actif': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['produit', 'entrepot', 'type_mouvement', 'quantite', 'motif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'input'}),
            'entrepot': forms.Select(attrs={'class': 'input'}),
            'type_mouvement': forms.Select(attrs={'class': 'input'}),
            'quantite': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'motif': forms.TextInput(attrs={'class': 'input', 'placeholder': _('Motif (optionnel)')}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['nom', 'emplacement', 'responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'emplacement': forms.TextInput(attrs={'class': 'input'}),
            'responsable': forms.Select(attrs={'class': 'input'}),
        }
