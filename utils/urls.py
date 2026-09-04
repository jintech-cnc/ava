from django.urls import path
from . import views
from . import import_views

app_name = 'utils'

urlpatterns = [
    # Exports
    path('export/produits/pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('export/produits/excel/', views.export_products_excel, name='export_products_excel'),
    path('export/commandes/<int:pk>/pdf/', views.export_order_pdf, name='export_order_pdf'),
    path('export/commandes/<int:pk>/excel/', views.export_order_excel, name='export_order_excel'),
    path('export/bons-commande/<int:pk>/pdf/', views.export_purchase_order_pdf, name='export_po_pdf'),
    path('export/bons-commande/<int:pk>/excel/', views.export_purchase_order_excel, name='export_po_excel'),
    path('export/mouvements/pdf/', views.export_movements_pdf, name='export_movements_pdf'),
    path('export/mouvements/excel/', views.export_movements_excel, name='export_movements_excel'),
    # Imports
    path('import/', import_views.import_dashboard, name='import_dashboard'),
    path('import/<str:model_name>/', import_views.import_data, name='import_data'),
    path('import/<str:model_name>/template/', import_views.download_template, name='import_template'),
    path('import/<str:model_name>/instructions/', import_views.import_instructions, name='import_instructions'),
]
