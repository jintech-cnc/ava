from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('produits/', views.product_list, name='product_list'),
    path('produits/nouveau/', views.product_form, name='product_create'),
    path('produits/<int:pk>/modifier/', views.product_form, name='product_edit'),
    path('produits/<int:pk>/supprimer/', views.product_delete, name='product_delete'),
    path('mouvements/', views.movement_list, name='movement_list'),
    path('mouvements/nouveau/', views.stock_movement_create, name='movement_create'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/nouveau/', views.category_form, name='category_create'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/modifier/', views.category_form, name='category_edit'),
    path('categories/<int:pk>/supprimer/', views.category_delete, name='category_delete'),
]
