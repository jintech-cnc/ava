"""
Crée/mets à jour un superuser depuis les variables d'environnement (pour Render).

Totalement idempotent : aucun create_superuser, manipulation directe du modèle User.

Variables d'environnement lues :
  DJANGO_SUPERUSER_USERNAME    (obligatoire)
  DJANGO_SUPERUSER_EMAIL       (optionnel)
  DJANGO_SUPERUSER_PASSWORD    (obligatoire)
  DJANGO_SUPERUSER_FIRST_NAME  (optionnel)
  DJANGO_SUPERUSER_LAST_NAME   (optionnel)
"""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée/mets à jour un superuser depuis les variables d'environnement."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', '')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', '')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_USERNAME ou DJANGO_SUPERUSER_PASSWORD non définis — skip."
            ))
            return

        # On utilise get_or_create pour éviter tout race condition avec create_superuser
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # Assure les flags superuser/staff quoi qu'il arrive
        user.is_staff = True
        user.is_superuser = True

        # Met à jour les champs optionnels si fournis
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        # Met toujours le mot de passe (nouveau build = on peut avoir changé le MDP)
        user.set_password(password)
        user.save()

        # Profil ADMIN
        self._update_profile(user)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' créé avec succès."))
        else:
            self.stdout.write(f"Superuser '{username}' déjà existant — mis à jour.")

    def _update_profile(self, user):
        """Assure que le profil existe et a le rôle ADMIN."""
        if hasattr(user, 'profile'):
            from accounts.models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            if profile.role != Profile.Role.ADMIN:
                profile.role = Profile.Role.ADMIN
                profile.save()
