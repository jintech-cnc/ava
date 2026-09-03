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
