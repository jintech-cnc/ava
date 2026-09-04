from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class AvaLoginForm(AuthenticationForm):
    """Formulaire de connexion avec libellés traduits et classes CSS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input',
            'placeholder': _("Nom d'utilisateur"),
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': 'input',
            'placeholder': _('Mot de passe'),
        })


class AvaLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = AvaLoginForm
    redirect_authenticated_user = True


# --- Vue d'administration simplifiée pour les utilisateurs non techniques ---
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

User = get_user_model()


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Tableau de bord administratif simplifié."""
    from orders.models import Client, Order
    from inventory.models import Warehouse

    total_users = User.objects.count()
    total_clients = Client.objects.count()
    total_orders = Order.objects.count()
    total_warehouses = Warehouse.objects.count()

    stats = {
        'total_users': total_users,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'total_warehouses': total_warehouses,
    }

    return render(request, 'accounts/admin_dashboard.html', {'stats': stats})


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin_user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    from .forms import CustomUserCreationForm

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Utilisateur créé avec succès.'))
            return redirect('accounts:user_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/admin_user_form.html', {'form': form, 'user_obj': None})


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    from .forms import CustomUserChangeForm

    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save()
            # Gestion du mot de passe optionnel
            new_password = request.POST.get('password1', '').strip()
            if new_password:
                user.set_password(new_password)
                user.save()
            messages.success(request, _('Utilisateur modifié avec succès.'))
            return redirect('accounts:user_list')
    else:
        form = CustomUserChangeForm(instance=user_obj)

    return render(request, 'accounts/admin_user_form.html', {'form': form, 'user_obj': user_obj})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, _('Vous ne pouvez pas supprimer votre propre compte.'))
            return redirect('accounts:user_list')
        user_obj.delete()
        messages.success(request, _('Utilisateur supprimé.'))
        return redirect('accounts:user_list')

    return render(request, 'accounts/admin_confirm_delete.html', {
        'object': user_obj,
        'object_type': 'utilisateur'
    })


@login_required
@user_passes_test(is_admin)
def client_list(request):
    from orders.models import Client
    clients = Client.objects.all().order_by('-cree_le')
    return render(request, 'accounts/admin_client_list.html', {'clients': clients})


@login_required
@user_passes_test(is_admin)
def client_create(request):
    from .forms import ClientAdminForm
    if request.method == 'POST':
        form = ClientAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Client créé avec succès.'))
            return redirect('accounts:client_list')
    else:
        form = ClientAdminForm()

    return render(request, 'accounts/admin_form.html', {
        'form': form,
        'title': _('Nouveau client'),
        'back_url': 'accounts:client_list'
    })


@login_required
@user_passes_test(is_admin)
def client_edit(request, pk):
    from orders.models import Client
    from .forms import ClientAdminForm

    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form = ClientAdminForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, _('Client modifié avec succès.'))
            return redirect('accounts:client_list')
    else:
        form = ClientAdminForm(instance=client)

    return render(request, 'accounts/admin_form.html', {
        'form': form,
        'title': _('Modifier le client'),
        'back_url': 'accounts:client_list'
    })


@login_required
@user_passes_test(is_admin)
def client_delete(request, pk):
    from orders.models import Client
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client.delete()
        messages.success(request, _('Client supprimé.'))
        return redirect('accounts:client_list')

    return render(request, 'accounts/admin_confirm_delete.html', {
        'object': client,
        'object_type': 'client'
    })


@login_required
@user_passes_test(is_admin)
def warehouse_list(request):
    from inventory.models import Warehouse
    warehouses = Warehouse.objects.all().order_by('nom')
    return render(request, 'accounts/admin_warehouse_list.html', {'warehouses': warehouses})


@login_required
@user_passes_test(is_admin)
def warehouse_create(request):
    from .forms import WarehouseAdminForm
    if request.method == 'POST':
        form = WarehouseAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Entrepôt créé avec succès.'))
            return redirect('accounts:warehouse_list')
    else:
        form = WarehouseAdminForm()

    return render(request, 'accounts/admin_form.html', {
        'form': form,
        'title': _('Nouvel entrepôt'),
        'back_url': 'accounts:warehouse_list'
    })


@login_required
@user_passes_test(is_admin)
def warehouse_edit(request, pk):
    from inventory.models import Warehouse
    from .forms import WarehouseAdminForm

    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        form = WarehouseAdminForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, _('Entrepôt modifié avec succès.'))
            return redirect('accounts:warehouse_list')
    else:
        form = WarehouseAdminForm(instance=warehouse)

    return render(request, 'accounts/admin_form.html', {
        'form': form,
        'title': _("Modifier l'entrepôt"),
        'back_url': 'accounts:warehouse_list'
    })


@login_required
@user_passes_test(is_admin)
def warehouse_delete(request, pk):
    from inventory.models import Warehouse
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, _('Entrepôt supprimé.'))
        return redirect('accounts:warehouse_list')

    return render(request, 'accounts/admin_confirm_delete.html', {
        'object': warehouse,
        'object_type': 'entrepôt'
    })
