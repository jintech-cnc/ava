from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.db.models import Q
import json

from .models import Order, Requisition, Client, OrderItem
from .forms import OrderForm, OrderItemFormSet, RequisitionForm, RequisitionItemFormSet
from inventory.models import Product, Warehouse, Category


@login_required
def pos_view(request):
    """Espace de vente quotidien (Point of Sale)."""
    produits = Product.objects.filter(actif=True).select_related('categorie')
    categories = Category.objects.all()
    clients = Client.objects.all()
    entrepots = Warehouse.objects.all()
    return render(request, 'orders/pos.html', {
        'produits': produits,
        'categories': categories,
        'clients': clients,
        'entrepots': entrepots,
    })


@login_required
def pos_create_order(request):
    """Crée une commande via l'interface POS."""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        client_id = data.get('client_id')
        entrepot_id = data.get('entrepot_id')
        items = data.get('items', [])
        
        if not items:
            return redirect('orders:pos')
            
        client = get_object_or_404(Client, pk=client_id)
        entrepot = get_object_or_404(Warehouse, pk=entrepot_id)
        
        commande = Order.objects.create(
            client=client,
            entrepot=entrepot,
            cree_par=request.user,
            statut=Order.Statut.CONFIRMEE
        )
        
        for item in items:
            produit = get_object_or_404(Product, pk=item['id'])
            OrderItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=item['quantity'],
                prix_unitaire=produit.prix_unitaire
            )
            
        return render(request, 'orders/_pos_success.html', {'commande': commande})
    
    return redirect('orders:pos')


@login_required
def order_list(request):
    query = request.GET.get('q', '').strip()
    commandes = Order.objects.select_related('client', 'entrepot').all()
    
    if query:
        commandes = commandes.filter(
            Q(pk__icontains=query) | 
            Q(client__nom__icontains=query) |
            Q(client__email__icontains=query) |
            Q(entrepot__nom__icontains=query)
        )
    
    return render(request, 'orders/order_list.html', {
        'commandes': commandes,
        'query': query
    })


@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            commande = form.save(commit=False)
            commande.cree_par = request.user
            commande.save()
            formset.instance = commande
            formset.save()
            messages.success(request, _('Commande #%(id)s enregistrée.') % {'id': commande.pk})
            return redirect('orders:order_list')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'orders/order_form.html', {'form': form, 'formset': formset})


@login_required
def order_detail(request, pk):
    commande = get_object_or_404(Order.objects.select_related('client', 'entrepot'), pk=pk)
    return render(request, 'orders/order_detail.html', {'commande': commande})


@login_required
def requisition_list(request):
    requisitions = Requisition.objects.select_related('demandeur', 'entrepot').all()
    return render(request, 'orders/requisition_list.html', {'requisitions': requisitions})


@login_required
def requisition_create(request):
    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        formset = RequisitionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            requisition = form.save(commit=False)
            requisition.demandeur = request.user
            requisition.save()
            formset.instance = requisition
            formset.save()
            messages.success(request, _('Réquisition #%(id)s soumise.') % {'id': requisition.pk})
            return redirect('orders:requisition_list')
    else:
        form = RequisitionForm()
        formset = RequisitionItemFormSet()

    return render(request, 'orders/requisition_form.html', {'form': form, 'formset': formset})


@login_required
def requisition_update_status(request, pk, statut):
    requisition = get_object_or_404(Requisition, pk=pk)
    valides = dict(Requisition.Statut.choices)
    if request.method == 'POST' and statut in valides:
        requisition.statut = statut
        if statut == Requisition.Statut.APPROUVEE:
            requisition.approuvee_par = request.user
        requisition.save()
        messages.success(request, _('Statut mis à jour : %(statut)s') % {'statut': valides[statut]})
    return redirect('orders:requisition_list')
