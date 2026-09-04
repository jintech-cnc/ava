"""
Ressources d'import pour django-import-export.
Permet l'import de données depuis CSV, Excel, JSON, etc.
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from django.contrib.auth import get_user_model

from inventory.models import Category, Product, Warehouse, StockMovement, Supplier, ReorderRule
from orders.models import Client, Order, OrderItem

User = get_user_model()


# ==========================================
# RESOURCES - CATEGORIES
# ==========================================

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'nom', 'description', 'is_hero')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# RESOURCES - PRODUITS
# ==========================================

class ProductResource(resources.ModelResource):
    categorie = fields.Field(
        column_name='categorie',
        attribute='categorie',
        widget=ForeignKeyWidget(Category, 'nom'),
    )
    
    class Meta:
        model = Product
        fields = (
            'id', 'reference', 'nom', 'description', 'categorie',
            'unite', 'prix_unitaire', 'seuil_alerte', 'actif'
        )
        import_id_fields = ('reference',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# RESOURCES - ENTREPOTS
# ==========================================

class WarehouseResource(resources.ModelResource):
    responsable = fields.Field(
        column_name='responsable',
        attribute='responsable',
        widget=ForeignKeyWidget(User, 'username'),
    )
    
    class Meta:
        model = Warehouse
        fields = ('id', 'nom', 'emplacement', 'responsable')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# RESOURCES - FOURNISSEURS
# ==========================================

class SupplierResource(resources.ModelResource):
    class Meta:
        model = Supplier
        fields = (
            'id', 'nom', 'contact', 'email', 'telephone',
            'adresse', 'notes', 'actif'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# RESOURCES - CLIENTS
# ==========================================

class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        fields = ('id', 'nom', 'email', 'telephone', 'adresse')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# RESOURCES - UTILISATEURS
# ==========================================

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
        import_id_fields = ('username',)
        skip_unchanged = True
        report_skipped = True
    
    def after_import_row(self, row, new_row, **kwargs):
        """Définir un mot de passe par défaut si l'utilisateur est nouveau."""
        if new_row.pk and not new_row.has_usable_password():
            new_row.set_password('changeme123')
            new_row.save()


# ==========================================
# RESOURCES - MOUVEMENTS DE STOCK
# ==========================================

class StockMovementResource(resources.ModelResource):
    produit = fields.Field(
        column_name='produit',
        attribute='produit',
        widget=ForeignKeyWidget(Product, 'reference'),
    )
    entrepot = fields.Field(
        column_name='entrepot',
        attribute='entrepot',
        widget=ForeignKeyWidget(Warehouse, 'nom'),
    )
    effectue_par = fields.Field(
        column_name='effectue_par',
        attribute='effectue_par',
        widget=ForeignKeyWidget(User, 'username'),
    )
    
    class Meta:
        model = StockMovement
        fields = (
            'id', 'produit', 'entrepot', 'type_mouvement',
            'quantite', 'motif', 'effectue_par', 'cree_le'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True
        exclude = ('cree_le',)


# ==========================================
# RESOURCES - REGLES DE REAPPROVISIONNEMENT
# ==========================================

class ReorderRuleResource(resources.ModelResource):
    produit = fields.Field(
        column_name='produit',
        attribute='produit',
        widget=ForeignKeyWidget(Product, 'reference'),
    )
    fournisseur = fields.Field(
        column_name='fournisseur',
        attribute='fournisseur',
        widget=ForeignKeyWidget(Supplier, 'nom'),
    )
    entrepot = fields.Field(
        column_name='entrepot',
        attribute='entrepot',
        widget=ForeignKeyWidget(Warehouse, 'nom'),
    )
    
    class Meta:
        model = ReorderRule
        fields = (
            'id', 'produit', 'fournisseur', 'entrepot',
            'quantite_min', 'quantite_cible',
            'delai_livraison_jours', 'actif'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True
