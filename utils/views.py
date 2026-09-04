"""
Vues pour l'export des documents.
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from inventory.models import Product, StockMovement, PurchaseOrder
from orders.models import Order
from .exports import (
    generate_product_list_pdf, generate_product_list_excel,
    generate_order_pdf, generate_order_excel,
    generate_purchase_order_pdf, generate_purchase_order_excel,
    generate_movement_pdf, generate_movement_excel,
)


def _get_language(request):
    """Récupère la langue de l'utilisateur ou 'fr' par défaut."""
    return getattr(request.user, 'profile', None) and \
           getattr(request.user.profile, 'langue_preferee', 'fr') or 'fr'


# ==========================================
# EXPORT PRODUITS
# ==========================================

@login_required
def export_products_pdf(request):
    """Export PDF de la liste des produits."""
    products = Product.objects.select_related('categorie').all()
    lang = _get_language(request)
    buffer = generate_product_list_pdf(products, lang)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="produits.pdf"'
    return response


@login_required
def export_products_excel(request):
    """Export Excel de la liste des produits."""
    products = Product.objects.select_related('categorie').all()
    lang = _get_language(request)
    buffer = generate_product_list_excel(products, lang)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="produits.xlsx"'
    return response


# ==========================================
# EXPORT COMMANDES CLIENTS
# ==========================================

@login_required
def export_order_pdf(request, pk):
    """Export PDF d'une commande client."""
    order = get_object_or_404(Order.objects.select_related('client', 'entrepot'), pk=pk)
    lang = _get_language(request)
    buffer = generate_order_pdf(order, lang)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commande_{pk}.pdf"'
    return response


@login_required
def export_order_excel(request, pk):
    """Export Excel d'une commande client."""
    order = get_object_or_404(Order.objects.select_related('client'), pk=pk)
    lang = _get_language(request)
    buffer = generate_order_excel(order, lang)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="commande_{pk}.xlsx"'
    return response


# ==========================================
# EXPORT BONS DE COMMANDE
# ==========================================

@login_required
def export_purchase_order_pdf(request, pk):
    """Export PDF d'un bon de commande fournisseur."""
    po = get_object_or_404(PurchaseOrder.objects.select_related('fournisseur', 'entrepot'), pk=pk)
    lang = _get_language(request)
    buffer = generate_purchase_order_pdf(po, lang)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BC_{po.reference}.pdf"'
    return response


@login_required
def export_purchase_order_excel(request, pk):
    """Export Excel d'un bon de commande fournisseur."""
    po = get_object_or_404(PurchaseOrder.objects.select_related('fournisseur'), pk=pk)
    lang = _get_language(request)
    buffer = generate_purchase_order_excel(po, lang)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="BC_{po.reference}.xlsx"'
    return response


# ==========================================
# EXPORT MOUVEMENTS DE STOCK
# ==========================================

@login_required
def export_movements_pdf(request):
    """Export PDF de l'historique des mouvements."""
    movements = StockMovement.objects.select_related(
        'produit', 'entrepot', 'effectue_par'
    ).all()[:500]
    lang = _get_language(request)
    buffer = generate_movement_pdf(movements, lang)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mouvements.pdf"'
    return response


@login_required
def export_movements_excel(request):
    """Export Excel de l'historique des mouvements."""
    movements = StockMovement.objects.select_related(
        'produit', 'entrepot', 'effectue_par'
    ).all()[:1000]
    lang = _get_language(request)
    buffer = generate_movement_excel(movements, lang)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="mouvements.xlsx"'
    return response
