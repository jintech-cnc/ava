from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    path('export/produits/pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('export/produits/excel/', views.export_products_excel, name='export_products_excel'),
    path('export/commandes/<int:pk>/pdf/', views.export_order_pdf, name='export_order_pdf'),
    path('export/commandes/<int:pk>/excel/', views.export_order_excel, name='export_order_excel'),
    path('export/bons-commande/<int:pk>/pdf/', views.export_purchase_order_pdf, name='export_po_pdf'),
    path('export/bons-commande/<int:pk>/excel/', views.export_purchase_order_excel, name='export_po_excel'),
    path('export/mouvements/pdf/', views.export_movements_pdf, name='export_movements_pdf'),
    path('export/mouvements/excel/', views.export_movements_excel, name='export_movements_excel'),
]
