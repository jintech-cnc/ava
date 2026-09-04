from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch, Count, Sum, F, OuterRef, Subquery, Value, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.utils import timezone
from django.db import models

from .models import Product, StockMovement, Category, Warehouse, Supplier, ReorderRule, PurchaseOrder, PurchaseOrderItem, Company, Stock
from .forms import ProductForm, StockMovementForm, CategoryForm, SupplierForm, ReorderRuleForm, PurchaseOrderForm, PurchaseOrderItemFormSet, CompanyForm
from utils.exports import (
    generate_product_list_pdf, generate_product_list_excel,
    generate_order_pdf, generate_order_excel,
    generate_purchase_order_pdf, generate_purchase_order_excel,
    generate_movement_pdf, generate_movement_excel,
    generate_requisition_pdf, generate_requisition_excel,
)


def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def get_cached_categories():
    """Cache des catégories pour éviter des requêtes répétées."""
    categories = cache.get('all_categories')
    if categories is None:
        categories = list(Category.objects.all().order_by('nom'))
        cache.set('all_categories', categories, 60 * 5)  # 5 min
    return categories


def get_current_company(request):
    """Récupère l'entreprise active pour l'utilisateur courant."""
    company = getattr(request, 'current_company', None)
    if company is not None:
        return company
    profile = getattr(request.user, 'profile', None)
    if profile and profile.company and profile.company.actif:
        return profile.company
    # Fallback : première entreprise active
    company = Company.objects.filter(actif=True).first()
    return company


def get_products_needing_reorder():
    """Liste les produits en alerte de stock (sous le seuil). Annoté pour éviter N+1."""
    stock_subquery = Stock.objects.filter(produit=OuterRef('pk')).values('produit').annotate(
        total=Sum('quantite')
    ).values('total')
    return Product.objects.select_related('categorie').prefetch_related(
        'stocks', 'reorder_rule__fournisseur'
    ).annotate(
        stock_total=Coalesce(Subquery(stock_subquery), Value(0), output_field=IntegerField()),
    ).filter(actif=True).filter(
        stock_total__lte=F('seuil_alerte')
    )


@login_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '')

    # Optimisation: select_related évite les requêtes N+1 sur la catégorie
    produits = Product.objects.select_related('categorie').only(
        'id', 'reference', 'nom', 'prix_unitaire', 'seuil_alerte', 'actif', 'unite',
        'categorie__nom', 'categorie__id'
    )
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | Q(reference__icontains=query)
        )
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)

    contexte = {
        'produits': produits,
        'categories': get_cached_categories(),
        'query': query,
        'categorie_id': categorie_id,
    }

    if is_htmx(request):
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


@login_required
def category_list(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    
    if query:
        categories = categories.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if is_htmx(request):
        return render(request, 'inventory/_category_table.html', {'categories': categories})
    return render(request, 'inventory/category_list.html', {'categories': categories, 'query': query})


@login_required
def category_form(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _('Catégorie « %(nom)s » enregistrée.') % {'nom': form.instance.nom}
            )
            if is_htmx(request):
                response = render(request, 'inventory/_toast_ok.html', {
                    'message': _('Catégorie enregistrée.')
                })
                response['HX-Trigger'] = 'categorieEnregistree'
                return response
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    
    contexte = {'form': form, 'category': category}
    template = 'inventory/_category_form.html' if is_htmx(request) else 'inventory/category_form.html'
    return render(request, template, contexte)


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    produits = category.produits.all()[:10]
    return render(request, 'inventory/category_detail.html', {
        'category': category,
        'produits': produits
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        nom = category.nom
        category.delete()
        messages.success(request, _('Catégorie « %(nom)s » supprimée.') % {'nom': nom})
        if is_htmx(request):
            return render(request, 'inventory/_toast_ok.html', {
                'message': _('Catégorie supprimée.')
            })
        return redirect('inventory:category_list')
    return render(request, 'inventory/_confirm_delete.html', {'object': category})


# ==========================================
# Réapprovisionnement
# ==========================================

@login_required
def reorder_dashboard(request):
    """Tableau de bord du réapprovisionnement."""
    regles = ReorderRule.objects.filter(actif=True).select_related('produit', 'fournisseur', 'entrepot')
    alertes = [r for r in regles if r.doit_reapprovisionner]
    
    bons_commande = PurchaseOrder.objects.select_related('fournisseur').order_by('-cree_le')[:10]
    fournisseurs = Supplier.objects.filter(actif=True)
    
    contexte = {
        'regles': regles,
        'alertes': alertes,
        'bons_commande': bons_commande,
        'fournisseurs': fournisseurs,
        'total_regles': regles.count(),
        'total_alertes': len(alertes),
    }
    return render(request, 'inventory/reorder_dashboard.html', contexte)


@login_required
def supplier_list(request):
    fournisseurs = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'fournisseurs': fournisseurs})


@login_required
def supplier_form(request, pk=None):
    supplier = get_object_or_404(Supplier, pk=pk) if pk else None
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, _('Fournisseur enregistré.'))
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/_supplier_form.html', {'form': form, 'supplier': supplier})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, _('Fournisseur supprimé.'))
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/_confirm_delete.html', {'object': supplier})


@login_required
def reorder_rule_list(request):
    regles = ReorderRule.objects.select_related('produit', 'fournisseur', 'entrepot').all()
    return render(request, 'inventory/reorder_rule_list.html', {'regles': regles})


@login_required
def reorder_rule_form(request, pk=None):
    regle = get_object_or_404(ReorderRule, pk=pk) if pk else None
    if request.method == 'POST':
        form = ReorderRuleForm(request.POST, instance=regle)
        if form.is_valid():
            form.save()
            messages.success(request, _('Règle de réapprovisionnement enregistrée.'))
            return redirect('inventory:reorder_rule_list')
    else:
        form = ReorderRuleForm(instance=regle)
    return render(request, 'inventory/_reorder_rule_form.html', {'form': form, 'regle': regle})


@login_required
def reorder_rule_delete(request, pk):
    regle = get_object_or_404(ReorderRule, pk=pk)
    if request.method == 'POST':
        regle.delete()
        messages.success(request, _('Règle supprimée.'))
        return redirect('inventory:reorder_rule_list')
    return render(request, 'inventory/_confirm_delete.html', {'object': regle})


@login_required
def purchase_order_list(request):
    query = request.GET.get('q', '').strip()
    bons = PurchaseOrder.objects.select_related('fournisseur', 'entrepot').all()
    if query:
        bons = bons.filter(
            Q(reference__icontains=query) |
            Q(fournisseur__nom__icontains=query)
        )
    return render(request, 'inventory/purchase_order_list.html', {
        'bons_commande': bons,
        'query': query,
    })


@login_required
def purchase_order_create(request, regle_id=None):
    """Crée un bon de commande (automatiquement depuis une règle si fourni)."""
    initial = {}
    lignes_initiales = []
    
    if regle_id:
        regle = get_object_or_404(ReorderRule, pk=regle_id)
        if regle.fournisseur:
            initial['fournisseur'] = regle.fournisseur
        if regle.entrepot:
            initial['entrepot'] = regle.entrepot
        if regle.quantite_a_commander > 0:
            lignes_initiales = [{
                'produit': regle.produit,
                'quantite_commandee': regle.quantite_a_commander,
                'prix_unitaire': regle.produit.prix_unitaire,
            }]
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            bon = form.save(commit=False)
            bon.cree_par = request.user
            bon.save()
            formset.instance = bon
            formset.save()
            messages.success(request, _('Bon de commande %(ref)s créé.') % {'ref': bon.reference})
            return redirect('inventory:purchase_order_detail', pk=bon.pk)
    else:
        form = PurchaseOrderForm(initial=initial)
        if lignes_initiales:
            formset = PurchaseOrderItemFormSet(initial=lignes_initiales)
        else:
            formset = PurchaseOrderItemFormSet()
    
    return render(request, 'inventory/purchase_order_form.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def purchase_order_detail(request, pk):
    bon = get_object_or_404(PurchaseOrder.objects.select_related('fournisseur', 'entrepot'), pk=pk)
    return render(request, 'inventory/purchase_order_detail.html', {'bon': bon})


@login_required
def purchase_order_update_status(request, pk, statut):
    bon = get_object_or_404(PurchaseOrder, pk=pk)
    valides = dict(PurchaseOrder.Statut.choices)
    if request.method == 'POST' and statut in valides:
        bon.statut = statut
        bon.save()
        messages.success(request, _('Statut mis à jour : %(statut)s') % {'statut': valides[statut]})
    return redirect('inventory:purchase_order_detail', pk=pk)


@login_required
def purchase_order_receive(request, pk):
    """Réceptionne un bon de commande et génère automatiquement les mouvements de stock."""
    bon = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        for ligne in bon.lignes.all():
            qte_recue = int(request.POST.get(f'qte_{ligne.pk}', ligne.quantite_commandee))
            ligne.quantite_recue = qte_recue
            ligne.save()
            
            if qte_recue > 0 and bon.entrepot:
                # Créer un mouvement d'entrée
                StockMovement.objects.create(
                    produit=ligne.produit,
                    entrepot=bon.entrepot,
                    type_mouvement=StockMovement.Type.ENTREE,
                    quantite=qte_recue,
                    motif=f'BC {bon.reference}',
                    effectue_par=request.user,
                )
        
        # Mettre à jour le statut
        toutes_livrees = all(l.est_complete for l in bon.lignes.all())
        partiellement = any(l.quantite_recue > 0 for l in bon.lignes.all())
        if toutes_livrees:
            bon.statut = PurchaseOrder.Statut.LIVREE
        elif partiellement:
            bon.statut = PurchaseOrder.Statut.PARTIELLEMENT_LIVREE
        bon.save()
        
        messages.success(request, _('Réception enregistrée.'))
        return redirect('inventory:purchase_order_detail', pk=pk)

    return redirect('inventory:purchase_order_detail', pk=pk)


# ==========================================
# Entreprises (multi-tenant)
# ==========================================

@login_required
def company_list(request):
    companies = Company.objects.all().order_by('-actif', 'nom')
    return render(request, 'inventory/company_list.html', {'companies': companies})


@login_required
def company_form(request, pk=None):
    company = get_object_or_404(Company, pk=pk) if pk else None
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, _('Entreprise enregistrée.'))
            return redirect('inventory:company_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'inventory/_company_form.html', {'form': form, 'company': company})


@login_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        messages.success(request, _('Entreprise supprimée.'))
        return redirect('inventory:company_list')
    return render(request, 'inventory/_confirm_delete.html', {'object': company})


# ==========================================
# Fiche de réquisition intelligente
# ==========================================

@login_required
def requisition_preview(request):
    """Affiche un aperçu de la fiche de réquisition pour les produits en rupture."""
    company = get_current_company(request)

    # Paramètre pour seuil personnalisé (optionnel)
    personnalise = request.GET.get('seuil_personnalise', '').strip()

    produits = get_products_needing_reorder()

    # Construire les lignes de réquisition
    lignes = []
    for p in produits:
        # Déterminer la quantité à commander
        qte_actuelle = p.stock_total
        regle = getattr(p, 'reorder_rule', None)
        if regle:
            qte_cible = regle.quantite_cible
            fournisseur = regle.fournisseur
        else:
            qte_cible = max(p.seuil_alerte * 2, 10)
            fournisseur = None

        qte_a_commander = max(0, qte_cible - qte_actuelle)

        lignes.append({
            'produit': p,
            'stock_actuel': qte_actuelle,
            'seuil': p.seuil_alerte,
            'qte_cible': qte_cible,
            'qte_a_commander': qte_a_commander,
            'fournisseur': fournisseur,
            'prix_unitaire': float(p.prix_unitaire),
            'estimation': float(p.prix_unitaire) * qte_a_commander,
        })

    # Grouper par fournisseur
    lignes_par_fournisseur = {}
    for ligne in lignes:
        key = ligne['fournisseur'].nom if ligne['fournisseur'] else 'Aucun fournisseur'
        lignes_par_fournisseur.setdefault(key, []).append(ligne)

    total_estime = sum(l['estimation'] for l in lignes)

    contexte = {
        'company': company,
        'lignes': lignes,
        'lignes_par_fournisseur': lignes_par_fournisseur,
        'total_estime': total_estime,
        'nb_produits': len(lignes),
    }
    return render(request, 'inventory/requisition_preview.html', contexte)


@login_required
def requisition_pdf(request):
    """Génère le PDF de la fiche de réquisition."""
    company = get_current_company(request)
    produits = get_products_needing_reorder()

    lignes = []
    for p in produits:
        regle = getattr(p, 'reorder_rule', None)
        if regle:
            qte_cible = regle.quantite_cible
            fournisseur = regle.fournisseur
        else:
            qte_cible = max(p.seuil_alerte * 2, 10)
            fournisseur = None

        qte_actuelle = p.stock_total
        qte_a_commander = max(0, qte_cible - qte_actuelle)

        lignes.append({
            'produit': p,
            'stock_actuel': qte_actuelle,
            'qte_cible': qte_cible,
            'qte_a_commander': qte_a_commander,
            'fournisseur': fournisseur,
            'prix_unitaire': float(p.prix_unitaire),
            'estimation': float(p.prix_unitaire) * qte_a_commander,
        })

    buffer = generate_requisition_pdf(lignes, company)
    filename = f"requisition_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def requisition_excel(request):
    """Génère le fichier Excel de la fiche de réquisition."""
    company = get_current_company(request)
    produits = get_products_needing_reorder()

    lignes = []
    for p in produits:
        regle = getattr(p, 'reorder_rule', None)
        if regle:
            qte_cible = regle.quantite_cible
            fournisseur = regle.fournisseur
        else:
            qte_cible = max(p.seuil_alerte * 2, 10)
            fournisseur = None

        qte_actuelle = p.stock_total
        qte_a_commander = max(0, qte_cible - qte_actuelle)

        lignes.append({
            'produit': p,
            'stock_actuel': qte_actuelle,
            'qte_cible': qte_cible,
            'qte_a_commander': qte_a_commander,
            'fournisseur': fournisseur,
            'prix_unitaire': float(p.prix_unitaire),
            'estimation': float(p.prix_unitaire) * qte_a_commander,
        })

    buffer = generate_requisition_excel(lignes, company)
    filename = f"requisition_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer.getvalue() if hasattr(buffer, 'getvalue') else buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def requisition_create_po(request):
    """Crée un bon de commande brouillon depuis la réquisition."""
    if request.method != 'POST':
        return redirect('inventory:requisition_preview')

    fournisseur_id = request.POST.get('fournisseur_id')
    lignes_data = request.POST.getlist('lignes')

    # Construire les lignes depuis les données POST
    lignes_produits = []
    for idx in range(0, len(lignes_data), 3):
        if idx + 2 >= len(lignes_data):
            break
        try:
            produit_id = int(lignes_data[idx])
            qte = int(lignes_data[idx + 1])
            prix = float(lignes_data[idx + 2])
            if qte > 0:
                lignes_produits.append({
                    'produit_id': produit_id,
                    'quantite_commandee': qte,
                    'prix_unitaire': prix,
                })
        except (ValueError, IndexError):
            continue

    if not lignes_produits:
        messages.warning(request, _('Aucune ligne valide pour créer le bon de commande.'))
        return redirect('inventory:requisition_preview')

    # Créer le bon de commande
    bon = PurchaseOrder.objects.create(
        fournisseur_id=fournisseur_id if fournisseur_id else None,
        statut=PurchaseOrder.Statut.BROUILLON,
        cree_par=request.user,
    )

    # Créer les lignes
    for ligne_data in lignes_produits:
        PurchaseOrderItem.objects.create(
            bon_commande=bon,
            produit_id=ligne_data['produit_id'],
            quantite_commandee=ligne_data['quantite_commandee'],
            prix_unitaire=ligne_data['prix_unitaire'],
        )

    messages.success(request, _('Bon de commande %(ref)s créé depuis la réquisition.') % {'ref': bon.reference})
    return redirect('inventory:purchase_order_detail', pk=bon.pk)


# ==========================================
# Vues d'export PDF/Excel (wrapper)
# ==========================================

@login_required
def export_products_pdf(request):
    """Export PDF de la liste des produits."""
    products = Product.objects.select_related('categorie').only(
        'id', 'reference', 'nom', 'categorie__nom', 'categorie__id',
        'prix_unitaire', 'seuil_alerte', 'actif', 'unite'
    )
    buffer = generate_product_list_pdf(products)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
def export_products_excel(request):
    """Export Excel de la liste des produits."""
    products = Product.objects.select_related('categorie').all()
    buffer = generate_product_list_excel(products)
    return HttpResponse(
        buffer.getvalue() if hasattr(buffer, 'getvalue') else buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@login_required
def export_movements_pdf(request):
    """Export PDF des mouvements de stock."""
    movements = StockMovement.objects.select_related(
        'produit', 'entrepot', 'effectue_par'
    ).order_by('-cree_le')[:500]
    buffer = generate_movement_pdf(movements)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
def export_movements_excel(request):
    """Export Excel des mouvements de stock."""
    movements = StockMovement.objects.select_related(
        'produit', 'entrepot', 'effectue_par'
    ).order_by('-cree_le')[:500]
    buffer = generate_movement_excel(movements)
    return HttpResponse(
        buffer.getvalue() if hasattr(buffer, 'getvalue') else buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@login_required
def export_order_pdf(request, pk):
    """Export PDF d'une commande."""
    from .models import Order
    order = get_object_or_404(Order.objects.prefetch_related('lignes__produit', 'client'), pk=pk)
    buffer = generate_order_pdf(order)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
def export_order_excel(request, pk):
    """Export Excel d'une commande."""
    from .models import Order
    order = get_object_or_404(Order.objects.prefetch_related('lignes__produit', 'client'), pk=pk)
    buffer = generate_order_excel(order)
    return HttpResponse(
        buffer.getvalue() if hasattr(buffer, 'getvalue') else buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@login_required
def export_purchase_order_pdf(request, pk):
    """Export PDF d'un bon de commande."""
    bon = get_object_or_404(PurchaseOrder.objects.select_related('fournisseur', 'entrepot').prefetch_related('lignes__produit'), pk=pk)
    buffer = generate_purchase_order_pdf(bon)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
def export_purchase_order_excel(request, pk):
    """Export Excel d'un bon de commande."""
    bon = get_object_or_404(PurchaseOrder.objects.select_related('fournisseur', 'entrepot').prefetch_related('lignes__produit'), pk=pk)
    buffer = generate_purchase_order_excel(bon)
    return HttpResponse(
        buffer.getvalue() if hasattr(buffer, 'getvalue') else buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
