from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrateur')
        MANAGER = 'manager', _('Gestionnaire de stock')
        STAFF = 'staff', _('Agent / Magasinier')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    telephone = models.CharField(max_length=30, blank=True)
    langue_preferee = models.CharField(
        max_length=10,
        choices=[('fr', 'Français'), ('en', 'English'), ('hi', 'हिन्दी'), ('zh-hans', '中文')],
        default='fr',
    )

    class Meta:
        verbose_name = _('Profil')
        verbose_name_plural = _('Profils')

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
