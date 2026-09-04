"""
Crée un superuser depuis les variables d'environnement (pour Render).

Variables d'environnement lues :
  DJANGO_SUPERUSER_USERNAME  (obligatoire)
  DJANGO_SUPERUSER_EMAIL     (optionnel)
  DJANGO_SUPERUSER_PASSWORD  (obligatoire)
  DJANGO_SUPERUSER_FIRST_NAME  (optionnel)
  DJANGO_SUPERUSER_LAST_NAME   (optionnel)

Idempotent : ne fait rien si l'utilisateur existe déjà.
"""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée un superuser depuis les variables d'environnement (idempotent)."

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
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' mis à jour."))
            else:
                self.stdout.write(f"Superuser '{username}' déjà présent — rien à faire.")
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Met le profil en ADMIN si le modèle Profile existe
        if hasattr(user, 'profile'):
            from accounts.models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            if profile.role != Profile.Role.ADMIN:
                profile.role = Profile.Role.ADMIN
                profile.save()

        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' créé avec succès."))
