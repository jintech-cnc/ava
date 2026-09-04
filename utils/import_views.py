"""
Vues pour l'import de données depuis CSV, Excel, JSON.
"""
import tablib
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from .imports import (
    CategoryResource, ProductResource, WarehouseResource,
    SupplierResource, ClientResource, UserResource,
    StockMovementResource, ReorderRuleResource
)


def is_admin(user):
    return user.is_authenticated and user.is_staff


SUPPORTED_FORMATS = ['csv', 'xlsx', 'xls', 'json', 'yaml', 'tsv']


def _get_resource_and_formats(model_name):
    """Retourne la ressource correspondant au modèle."""
    resources = {
        'categories': CategoryResource,
        'produits': ProductResource,
        'entrepots': WarehouseResource,
        'fournisseurs': SupplierResource,
        'clients': ClientResource,
        'utilisateurs': UserResource,
        'mouvements': StockMovementResource,
        'regles': ReorderRuleResource,
    }
    return resources.get(model_name)


@login_required
@user_passes_test(is_admin)
def import_dashboard(request):
    """Tableau de bord des imports disponibles."""
    return render(request, 'utils/import_dashboard.html')


@login_required
@user_passes_test(is_admin)
def import_data(request, model_name):
    """Vue générique d'import de données."""
    resource_class = _get_resource_and_formats(model_name)
    if not resource_class:
        messages.error(request, _('Type de modèle invalide.'))
        return redirect('utils:import_dashboard')
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_format = request.POST.get('format', 'auto')
        
        try:
            # Lecture du fichier
            data = tablib.Dataset()
            file_content = uploaded_file.read()
            
            if file_format == 'auto' or not file_format:
                # Détection automatique du format
                file_name = uploaded_file.name.lower()
                if file_name.endswith('.csv'):
                    data.load(file_content.decode('utf-8'), format='csv')
                elif file_name.endswith('.xlsx'):
                    data.load(file_content, format='xlsx')
                elif file_name.endswith('.xls'):
                    data.load(file_content, format='xls')
                elif file_name.endswith('.json'):
                    data.load(file_content.decode('utf-8'), format='json')
                elif file_name.endswith('.yaml') or file_name.endswith('.yml'):
                    data.load(file_content.decode('utf-8'), format='yaml')
                elif file_name.endswith('.tsv'):
                    data.load(file_content.decode('utf-8'), format='tsv')
                else:
                    # Essayer CSV par défaut
                    data.load(file_content.decode('utf-8'), format='csv')
            elif file_format == 'csv':
                data.load(file_content.decode('utf-8'), format='csv')
            elif file_format == 'xlsx':
                data.load(file_content, format='xlsx')
            elif file_format == 'json':
                data.load(file_content.decode('utf-8'), format='json')
            elif file_format == 'yaml':
                data.load(file_content.decode('utf-8'), format='yaml')
            elif file_format == 'tsv':
                data.load(file_content.decode('utf-8'), format='tsv')
            else:
                data.load(file_content.decode('utf-8'), format='csv')
            
            # Import via la ressource
            resource = resource_class()
            result = resource.import_data(data, dry_run=False, raise_errors=False)
            
            # Messages de résultat
            if result.has_errors():
                error_messages = []
                for row_num, errors in enumerate(result.row_errors(), 1):
                    for error in errors[1]:
                        error_messages.append(_('Ligne %(row)s: %(error)s') % {
                            'row': row_num, 'error': str(error.error)
                        })
                messages.error(
                    request,
                    _('%(count)s erreurs rencontrées :') % {'count': len(error_messages)}
                )
                for err in error_messages[:5]:
                    messages.warning(request, err)
            else:
                messages.success(
                    request,
                    _('Import réussi ! %(count)s lignes importées, %(updated)s mises à jour.') % {
                        'count': result.totals['new'],
                        'updated': result.totals['update'],
                    }
                )
            
            return render(request, 'utils/import_result.html', {
                'result': result,
                'model_name': model_name,
            })
            
        except Exception as e:
            messages.error(request, _('Erreur lors de l\'import : %(error)s') % {'error': str(e)})
            return redirect('utils:import_data', model_name=model_name)
    
    return render(request, 'utils/import_form.html', {
        'model_name': model_name,
        'supported_formats': SUPPORTED_FORMATS,
    })


@login_required
@user_passes_test(is_admin)
def download_template(request, model_name):
    """Génère et télécharge un template Excel pour l'import."""
    resource_class = _get_resource_and_formats(model_name)
    if not resource_class:
        messages.error(request, _('Type de modèle invalide.'))
        return redirect('utils:import_dashboard')
    
    resource = resource_class()
    # Récupérer les en-têtes des colonnes
    headers = resource.get_export_headers()
    
    # Créer un template Excel avec les en-têtes
    headers_row = []
    for h in headers:
        headers_row.append(h)
    
    headers_export = tablib.Dataset(*[tuple(headers_row)], headers=headers_row)
    headers_data = headers_export.export('xlsx')
    
    response = HttpResponse(
        headers_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="template_{model_name}.xlsx"'
    return response


@login_required
@user_passes_test(is_admin)
def import_instructions(request, model_name):
    """Affiche les instructions d'import pour un modèle."""
    columns_info = {
        'categories': [
            ('nom', 'Nom de la catégorie (obligatoire, unique)', 'text'),
            ('description', 'Description', 'text'),
            ('is_hero', 'Catégorie en héro (true/false)', 'boolean'),
        ],
        'produits': [
            ('reference', 'Référence unique (obligatoire)', 'text'),
            ('nom', 'Nom du produit (obligatoire)', 'text'),
            ('description', 'Description', 'text'),
            ('categorie', 'Nom de la catégorie (doit exister)', 'text'),
            ('unite', 'Unité (pièce, kg, etc.)', 'text'),
            ('prix_unitaire', 'Prix unitaire', 'number'),
            ('seuil_alerte', 'Seuil d\'alerte de stock', 'number'),
            ('actif', 'Actif (true/false)', 'boolean'),
        ],
        'entrepots': [
            ('nom', 'Nom de l\'entrepôt (obligatoire, unique)', 'text'),
            ('emplacement', 'Emplacement', 'text'),
            ('responsable', 'Nom d\'utilisateur du responsable', 'text'),
        ],
        'fournisseurs': [
            ('nom', 'Nom du fournisseur (obligatoire)', 'text'),
            ('contact', 'Personne de contact', 'text'),
            ('email', 'Email', 'text'),
            ('telephone', 'Téléphone', 'text'),
            ('adresse', 'Adresse', 'text'),
            ('notes', 'Notes', 'text'),
            ('actif', 'Actif (true/false)', 'boolean'),
        ],
        'clients': [
            ('nom', 'Nom du client (obligatoire)', 'text'),
            ('email', 'Email', 'text'),
            ('telephone', 'Téléphone', 'text'),
            ('adresse', 'Adresse', 'text'),
        ],
        'utilisateurs': [
            ('username', 'Nom d\'utilisateur (obligatoire, unique)', 'text'),
            ('email', 'Email', 'text'),
            ('first_name', 'Prénom', 'text'),
            ('last_name', 'Nom', 'text'),
            ('is_active', 'Actif (true/false)', 'boolean'),
            ('is_staff', 'Administrateur (true/false)', 'boolean'),
        ],
        'mouvements': [
            ('produit', 'Référence du produit (doit exister)', 'text'),
            ('entrepot', 'Nom de l\'entrepôt (doit exister)', 'text'),
            ('type_mouvement', 'Type (entree/sortie/ajustement/transfert)', 'choice'),
            ('quantite', 'Quantité (obligatoire)', 'number'),
            ('motif', 'Motif', 'text'),
            ('effectue_par', 'Nom d\'utilisateur', 'text'),
        ],
        'regles': [
            ('produit', 'Référence du produit (doit exister, unique)', 'text'),
            ('fournisseur', 'Nom du fournisseur', 'text'),
            ('entrepot', 'Nom de l\'entrepôt', 'text'),
            ('quantite_min', 'Stock minimum', 'number'),
            ('quantite_cible', 'Stock cible', 'number'),
            ('delai_livraison_jours', 'Délai de livraison en jours', 'number'),
            ('actif', 'Actif (true/false)', 'boolean'),
        ],
    }
    
    return render(request, 'utils/import_instructions.html', {
        'model_name': model_name,
        'columns': columns_info.get(model_name, []),
    })
