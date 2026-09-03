from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Client, Order, OrderItem, Requisition, RequisitionItem


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'email', 'telephone', 'adresse']
        widgets = {f: forms.TextInput(attrs={'class': 'input'}) for f in ['nom', 'telephone', 'adresse']}
        widgets['email'] = forms.EmailInput(attrs={'class': 'input'})


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'entrepot', 'statut', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'input'}),
            'entrepot': forms.Select(attrs={'class': 'input'}),
            'statut': forms.Select(attrs={'class': 'input'}),
            'notes': forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'produit': forms.Select(attrs={'class': 'input'}),
            'quantite': forms.NumberInput(attrs={'class': 'input', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=3, can_delete=True,
)


class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ['entrepot', 'service', 'justification']
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'input'}),
            'service': forms.TextInput(attrs={'class': 'input', 'placeholder': _('Ex. Atelier, Comptabilité...')}),
            'justification': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }


class RequisitionItemForm(forms.ModelForm):
    class Meta:
        model = RequisitionItem
        fields = ['produit', 'quantite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'input'}),
            'quantite': forms.NumberInput(attrs={'class': 'input', 'min': 1}),
        }


RequisitionItemFormSet = inlineformset_factory(
    Requisition, RequisitionItem, form=RequisitionItemForm, extra=3, can_delete=True,
)
