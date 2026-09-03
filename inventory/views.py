from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from .models import Product, StockMovement, Category, Warehouse
from .forms import ProductForm, StockMovementForm


def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


@login_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '')

    produits = Product.objects.select_related('categorie').all()
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | Q(reference__icontains=query)
        )
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)

    contexte = {
        'produits': produits,
        'categories': Category.objects.all(),
        'query': query,
        'categorie_id': categorie_id,
    }

    if is_htmx(request):
        # Ne renvoie que le tableau, pour un rafraîchissement fluide sans recharger la page
        return render(request, 'inventory/_product_table.html', contexte)
    return render(request, 'inventory/product_list.html', contexte)


@login_required
def product_form(request, pk=None):
    produit = get_object_or_404(Product, pk=pk) if pk else None

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _('Produit « %(nom)s » enregistré avec succès.') % {'nom': form.instance.nom},
            )
            if is_htmx(request):
                response = render(request, 'inventory/_toast_ok.html', {
                    'message': _('Produit enregistré.')
                })
                response['HX-Trigger'] = 'produitEnregistre'
                return response
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=produit)

    contexte = {'form': form, 'produit': produit}
    template = 'inventory/_product_form.html' if is_htmx(request) else 'inventory/product_form.html'
    return render(request, template, contexte)


@login_required
def product_delete(request, pk):
    produit = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, _('Produit « %(nom)s » supprimé.') % {'nom': nom})
        if is_htmx(request):
            return render(request, 'inventory/_toast_ok.html', {
                'message': _('Produit supprimé.')
            })
        return redirect('inventory:product_list')
    return render(request, 'inventory/_confirm_delete.html', {'produit': produit})


@login_required
def stock_movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.effectue_par = request.user
            mouvement.save()
            messages.success(request, _('Mouvement de stock enregistré.'))
            if is_htmx(request):
                response = render(request, 'inventory/_toast_ok.html', {
                    'message': _('Mouvement enregistré : %(produit)s') % {'produit': mouvement.produit}
                })
                response['HX-Trigger'] = 'mouvementEnregistre'
                return response
            return redirect('inventory:product_list')
    else:
        form = StockMovementForm()

    contexte = {'form': form}
    template = 'inventory/_stock_movement_form.html' if is_htmx(request) else 'inventory/stock_movement_form.html'
    return render(request, template, contexte)


@login_required
def movement_list(request):
    mouvements = StockMovement.objects.select_related('produit', 'entrepot', 'effectue_par')[:100]
    return render(request, 'inventory/movement_list.html', {'mouvements': mouvements})
