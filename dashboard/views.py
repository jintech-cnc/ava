from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import render

from inventory.models import Product, StockMovement, Warehouse
from orders.models import Order, Requisition


@login_required
def home(request):
    produits = Product.objects.all()
    produits_en_alerte = [p for p in produits if p.en_alerte]

    contexte = {
        'nb_produits': produits.count(),
        'nb_entrepots': Warehouse.objects.count(),
        'nb_produits_alerte': len(produits_en_alerte),
        'produits_alerte': produits_en_alerte[:8],
        'nb_commandes_attente': Order.objects.filter(statut='en_attente').count(),
        'nb_requisitions_soumises': Requisition.objects.filter(statut='soumise').count(),
        'derniers_mouvements': StockMovement.objects.select_related('produit', 'entrepot')[:8],
        'dernieres_commandes': Order.objects.select_related('client')[:5],
    }
    return render(request, 'dashboard/dashboard.html', contexte)
