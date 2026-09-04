"""
Crée un superuser depuis les variables d'environnement (pour Render).

Variables d'environnement lues :
  DJANGO_SUPERUSER_USERNAME  (obligatoire)
  DJANGO_SUPERUSER_EMAIL     (optionnel)
  DJANGO_SUPERUSER_PASSWORD  (obligatoire)
  DJANGO_SUPERUSER_FIRST_NAME  (optionnel)
  DJANGO_SUPERUSER_LAST_NAME   (optionnel)

Totalement idempotent : gère le cas où l'user existe déjà (race condition,
build rerun, etc.).
"""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


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

        # --- user existe déjà : on met à jour --------------------------------
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            updated = False
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                updated = True
            if email and user.email != email:
                user.email = email
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if password and not user.has_usable_password():
                user.set_password(password)
                updated = True
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' mis à jour."))
            else:
                self.stdout.write(f"Superuser '{username}' déjà présent — rien à faire.")
            self._update_profile(user)
            return

        # --- user n'existe pas : on crée ------------------------------------
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except CommandError:
            # Race condition : un autre processus l'a créé entre-temps
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(
                f"Superuser '{username}' existait déjà (race) — mise à jour."
            ))
            # Met à jour les champs au cas où
            user.is_superuser = True
            user.is_staff = True
            user.email = email or user.email
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.set_password(password)
            user.save()

        self._update_profile(user)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' créé avec succès."))

    def _update_profile(self, user):
        """Assure que le profil existe et a le rôle ADMIN."""
        if hasattr(user, 'profile'):
            from accounts.models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            if profile.role != Profile.Role.ADMIN:
                profile.role = Profile.Role.ADMIN
                profile.save()
