from django.contrib import admin
from .models import Category, Warehouse, Product, Stock, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'emplacement', 'responsable')
    search_fields = ('nom',)


class StockInline(admin.TabularInline):
    model = Stock
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('reference', 'nom', 'categorie', 'prix_unitaire', 'quantite_totale', 'en_alerte', 'actif')
    list_filter = ('categorie', 'actif')
    search_fields = ('reference', 'nom')
    inlines = [StockInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('produit', 'entrepot', 'type_mouvement', 'quantite', 'effectue_par', 'cree_le')
    list_filter = ('type_mouvement', 'entrepot')
    date_hierarchy = 'cree_le'
