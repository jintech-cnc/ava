from django.contrib.auth import views as auth_views
from django.urls import path
from .views import AvaLoginView, admin_dashboard, user_list, user_create, user_edit, user_delete
from .views import client_list, client_create, client_edit, client_delete
from .views import warehouse_list, warehouse_create, warehouse_edit, warehouse_delete

app_name = 'accounts'

urlpatterns = [
    path('connexion/', AvaLoginView.as_view(), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Réinitialisation du mot de passe
    path('mot-de-passe/oublie/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/accounts/mot-de-passe/oublie/envoye/',
    ), name='password_reset'),
    path('mot-de-passe/oublie/envoye/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('mot-de-passe/reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/accounts/mot-de-passe/reinitialise/',
    ), name='password_reset_confirm'),
    path('mot-de-passe/reinitialise/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),

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
