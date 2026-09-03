from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from inventory.models import Product, Warehouse


class Client(models.Model):
    nom = models.CharField(_('nom'), max_length=150)
    email = models.EmailField(_('email'), blank=True)
    telephone = models.CharField(_('téléphone'), max_length=30, blank=True)
    adresse = models.CharField(_('adresse'), max_length=255, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Order(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', _('En attente')
        CONFIRMEE = 'confirmee', _('Confirmée')
        EXPEDIEE = 'expediee', _('Expédiée')
        ANNULEE = 'annulee', _('Annulée')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    entrepot = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, related_name='commandes')
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    notes = models.TextField(_('notes'), blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('créée par'),
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')
        ordering = ['-cree_le']

    def __str__(self):
        return f'Commande #{self.pk} — {self.client}'

    @property
    def montant_total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())


class OrderItem(models.Model):
    commande = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='lignes_commande')
    quantite = models.PositiveIntegerField(_('quantité'), default=1)
    prix_unitaire = models.DecimalField(_('prix unitaire'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Ligne de commande')
        verbose_name_plural = _('Lignes de commande')

    def __str__(self):
        return f'{self.produit} x{self.quantite}'

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix_unitaire
        super().save(*args, **kwargs)


class Requisition(models.Model):
    """Demande interne de matériel/produits par un service ou un employé."""

    class Statut(models.TextChoices):
        SOUMISE = 'soumise', _('Soumise')
        APPROUVEE = 'approuvee', _('Approuvée')
        REJETEE = 'rejetee', _('Rejetée')
        LIVREE = 'livree', _('Livrée')

    demandeur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requisitions',
        verbose_name=_('demandeur'),
    )
    entrepot = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, related_name='requisitions')
    service = models.CharField(_('service / département'), max_length=100, blank=True)
    justification = models.TextField(_('justification'), blank=True)
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.SOUMISE)
    approuvee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='requisitions_approuvees', verbose_name=_('approuvée par'),
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Réquisition')
        verbose_name_plural = _('Réquisitions')
        ordering = ['-cree_le']

    def __str__(self):
        return f'Réquisition #{self.pk} — {self.demandeur}'


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='lignes_requisition')
    quantite = models.PositiveIntegerField(_('quantité'), default=1)

    class Meta:
        verbose_name = _('Ligne de réquisition')
        verbose_name_plural = _('Lignes de réquisition')

    def __str__(self):
        return f'{self.produit} x{self.quantite}'
