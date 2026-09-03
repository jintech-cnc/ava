from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Warehouse(models.Model):
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    emplacement = models.CharField(_('emplacement'), max_length=200, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='entrepots_geres', verbose_name=_('responsable'),
    )

    class Meta:
        verbose_name = _('Entrepôt')
        verbose_name_plural = _('Entrepôts')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Product(models.Model):
    reference = models.CharField(_('référence'), max_length=50, unique=True)
    nom = models.CharField(_('nom'), max_length=150)
    description = models.TextField(_('description'), blank=True)
    categorie = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='produits',
        verbose_name=_('catégorie'),
    )
    unite = models.CharField(_('unité'), max_length=20, default=_('pièce'))
    prix_unitaire = models.DecimalField(_('prix unitaire'), max_digits=10, decimal_places=2, default=0)
    seuil_alerte = models.PositiveIntegerField(
        _("seuil d'alerte"), default=10,
        help_text=_('Quantité en dessous de laquelle une alerte de rupture est déclenchée'),
    )
    actif = models.BooleanField(_('actif'), default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['nom']

    def __str__(self):
        return f'{self.reference} — {self.nom}'

    def get_absolute_url(self):
        return reverse('inventory:product_detail', args=[self.pk])

    @property
    def quantite_totale(self):
        total = self.stocks.aggregate(total=models.Sum('quantite'))['total']
        return total or 0

    @property
    def en_alerte(self):
        return self.quantite_totale <= self.seuil_alerte


class Stock(models.Model):
    """Quantité d'un produit dans un entrepôt donné."""
    produit = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    entrepot = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    quantite = models.IntegerField(_('quantité'), default=0)

    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        unique_together = ('produit', 'entrepot')

    def __str__(self):
        return f'{self.produit} @ {self.entrepot}: {self.quantite}'


class StockMovement(models.Model):
    class Type(models.TextChoices):
        ENTREE = 'entree', _('Entrée')
        SORTIE = 'sortie', _('Sortie')
        AJUSTEMENT = 'ajustement', _('Ajustement')
        TRANSFERT = 'transfert', _('Transfert')

    produit = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='mouvements')
    entrepot = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(_('type'), max_length=20, choices=Type.choices)
    quantite = models.IntegerField(_('quantité'), help_text=_('Toujours positive ; le sens dépend du type'))
    motif = models.CharField(_('motif'), max_length=200, blank=True)
    effectue_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('effectué par'),
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-cree_le']

    def __str__(self):
        return f'{self.get_type_mouvement_display()} · {self.produit} · {self.quantite}'

    def save(self, *args, **kwargs):
        """Applique le mouvement sur le stock correspondant avant sauvegarde."""
        creation = self._state.adding
        super().save(*args, **kwargs)
        if creation:
            stock, _created = Stock.objects.get_or_create(
                produit=self.produit, entrepot=self.entrepot, defaults={'quantite': 0}
            )
            if self.type_mouvement == self.Type.ENTREE:
                stock.quantite += self.quantite
            elif self.type_mouvement == self.Type.SORTIE:
                stock.quantite -= self.quantite
            elif self.type_mouvement == self.Type.AJUSTEMENT:
                stock.quantite = self.quantite
            stock.save()
