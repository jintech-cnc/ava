from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Product, StockMovement, Category, Warehouse, Supplier, ReorderRule, PurchaseOrder, PurchaseOrderItem, Company


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
        fields = ['nom', 'description', 'image', 'is_hero']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'input'}),
            'is_hero': forms.CheckboxInput(attrs={'class': 'checkbox'}),
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


# ==========================================
# Formulaires de réapprovisionnement
# ==========================================

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['nom', 'contact', 'email', 'telephone', 'adresse', 'notes', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'contact': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'telephone': forms.TextInput(attrs={'class': 'input'}),
            'adresse': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'actif': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class ReorderRuleForm(forms.ModelForm):
    class Meta:
        model = ReorderRule
        fields = ['produit', 'fournisseur', 'entrepot', 'quantite_min', 'quantite_cible', 'delai_livraison_jours', 'actif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'input'}),
            'fournisseur': forms.Select(attrs={'class': 'input'}),
            'entrepot': forms.Select(attrs={'class': 'input'}),
            'quantite_min': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'quantite_cible': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'delai_livraison_jours': forms.NumberInput(attrs={'class': 'input', 'min': 1}),
            'actif': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['fournisseur', 'entrepot', 'date_commande', 'date_livraison_prevue', 'notes']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'input'}),
            'entrepot': forms.Select(attrs={'class': 'input'}),
            'date_commande': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['produit', 'quantite_commandee', 'prix_unitaire']
        widgets = {
            'produit': forms.Select(attrs={'class': 'input'}),
            'quantite_commandee': forms.NumberInput(attrs={'class': 'input', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemForm,
    extra=3, can_delete=True,
)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'nom', 'slogan', 'logo', 'adresse', 'telephone', 'email', 'site_web',
            'rccm', 'id_national', 'numero_impot',
            'devise', 'separateur_milliers', 'prefixe_symbole', 'mentions_footer', 'actif',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'slogan': forms.TextInput(attrs={'class': 'input'}),
            'logo': forms.FileInput(attrs={'class': 'input'}),
            'adresse': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
            'telephone': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'site_web': forms.URLInput(attrs={'class': 'input'}),
            'rccm': forms.TextInput(attrs={'class': 'input'}),
            'id_national': forms.TextInput(attrs={'class': 'input'}),
            'numero_impot': forms.TextInput(attrs={'class': 'input'}),
            'devise': forms.TextInput(attrs={'class': 'input'}),
            'separateur_milliers': forms.TextInput(attrs={'class': 'input'}),
            'prefixe_symbole': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'mentions_footer': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
