from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('commandes/', views.order_list, name='order_list'),
    path('commandes/nouvelle/', views.order_create, name='order_create'),
    path('commandes/<int:pk>/', views.order_detail, name='order_detail'),
    path('requisitions/', views.requisition_list, name='requisition_list'),
    path('requisitions/nouvelle/', views.requisition_create, name='requisition_create'),
    path('requisitions/<int:pk>/statut/<str:statut>/', views.requisition_update_status, name='requisition_status'),
]
