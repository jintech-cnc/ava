from django.contrib.auth import views as auth_views
from django.urls import path
from .views import AvaLoginView

app_name = 'accounts'

urlpatterns = [
    path('connexion/', AvaLoginView.as_view(), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
]
