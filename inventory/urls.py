from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Produits
    path('produits/', views.product_list, name='product_list'),
    path('produits/nouveau/', views.product_form, name='product_create'),
    path('produits/<int:pk>/modifier/', views.product_form, name='product_edit'),
    path('produits/<int:pk>/supprimer/', views.product_delete, name='product_delete'),
    # Mouvements de stock
    path('mouvements/', views.movement_list, name='movement_list'),
    path('mouvements/nouveau/', views.stock_movement_create, name='movement_create'),
    # Catégories
    path('categories/', views.category_list, name='category_list'),
    path('categories/nouveau/', views.category_form, name='category_create'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/modifier/', views.category_form, name='category_edit'),
    path('categories/<int:pk>/supprimer/', views.category_delete, name='category_delete'),
    # Réapprovisionnement
    path('reapprovisionnement/', views.reorder_dashboard, name='reorder_dashboard'),
    # Fournisseurs
    path('reapprovisionnement/fournisseurs/', views.supplier_list, name='supplier_list'),
    path('reapprovisionnement/fournisseurs/nouveau/', views.supplier_form, name='supplier_create'),
    path('reapprovisionnement/fournisseurs/<int:pk>/modifier/', views.supplier_form, name='supplier_edit'),
    path('reapprovisionnement/fournisseurs/<int:pk>/supprimer/', views.supplier_delete, name='supplier_delete'),
    # Règles de réapprovisionnement
    path('reapprovisionnement/regles/', views.reorder_rule_list, name='reorder_rule_list'),
    path('reapprovisionnement/regles/nouveau/', views.reorder_rule_form, name='reorder_rule_create'),
    path('reapprovisionnement/regles/<int:pk>/modifier/', views.reorder_rule_form, name='reorder_rule_edit'),
    path('reapprovisionnement/regles/<int:pk>/supprimer/', views.reorder_rule_delete, name='reorder_rule_delete'),
    # Bons de commande
    path('reapprovisionnement/commandes/', views.purchase_order_list, name='purchase_order_list'),
    path('reapprovisionnement/commandes/nouveau/', views.purchase_order_create, name='purchase_order_create'),
    path('reapprovisionnement/commandes/depuis/<int:regle_id>/', views.purchase_order_create, name='purchase_order_from_rule'),
    path('reapprovisionnement/commandes/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('reapprovisionnement/commandes/<int:pk>/statut/<str:statut>/', views.purchase_order_update_status, name='purchase_order_status'),
    path('reapprovisionnement/commandes/<int:pk>/receptionner/', views.purchase_order_receive, name='purchase_order_receive'),
    # Fiche de réquisition
    path('reapprovisionnement/requisition/', views.requisition_preview, name='requisition_preview'),
    path('reapprovisionnement/requisition/pdf/', views.requisition_pdf, name='requisition_pdf'),
    path('reapprovisionnement/requisition/excel/', views.requisition_excel, name='requisition_excel'),
    path('reapprovisionnement/requisition/creer-bc/', views.requisition_create_po, name='requisition_create_po'),
    # Exports PDF/Excel
    path('exports/produits/pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('exports/produits/excel/', views.export_products_excel, name='export_products_excel'),
    path('exports/mouvements/pdf/', views.export_movements_pdf, name='export_movements_pdf'),
    path('exports/mouvements/excel/', views.export_movements_excel, name='export_movements_excel'),
    path('exports/commandes/<int:pk>/pdf/', views.export_order_pdf, name='export_order_pdf'),
    path('exports/commandes/<int:pk>/excel/', views.export_order_excel, name='export_order_excel'),
    path('exports/bc/<int:pk>/pdf/', views.export_purchase_order_pdf, name='export_po_pdf'),
    path('exports/bc/<int:pk>/excel/', views.export_purchase_order_excel, name='export_po_excel'),
    # Entreprises
    path('entreprises/', views.company_list, name='company_list'),
    path('entreprises/nouveau/', views.company_form, name='company_create'),
    path('entreprises/<int:pk>/modifier/', views.company_form, name='company_edit'),
    path('entreprises/<int:pk>/supprimer/', views.company_delete, name='company_delete'),
]