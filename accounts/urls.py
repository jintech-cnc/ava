from django.contrib.auth import views as auth_views
from django.urls import path
from .views import AvaLoginView, admin_dashboard, user_list, user_create, user_edit, user_delete
from .views import client_list, client_create, client_edit, client_delete
from .views import warehouse_list, warehouse_create, warehouse_edit, warehouse_delete

app_name = 'accounts'

urlpatterns = [
    path('connexion/', AvaLoginView.as_view(), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    # Admin simplifié
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/utilisateurs/', user_list, name='user_list'),
    path('admin/utilisateurs/nouveau/', user_create, name='user_create'),
    path('admin/utilisateurs/<int:pk>/modifier/', user_edit, name='user_edit'),
    path('admin/utilisateurs/<int:pk>/supprimer/', user_delete, name='user_delete'),
    path('admin/clients/', client_list, name='client_list'),
    path('admin/clients/nouveau/', client_create, name='client_create'),
    path('admin/clients/<int:pk>/modifier/', client_edit, name='client_edit'),
    path('admin/clients/<int:pk>/supprimer/', client_delete, name='client_delete'),
    path('admin/entrepots/', warehouse_list, name='warehouse_list'),
    path('admin/entrepots/nouveau/', warehouse_create, name='warehouse_create'),
    path('admin/entrepots/<int:pk>/modifier/', warehouse_edit, name='warehouse_edit'),
    path('admin/entrepots/<int:pk>/supprimer/', warehouse_delete, name='warehouse_delete'),
]
