from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """Profil d'entreprise — chaque entreprise a ses propres infos sur les documents."""
    nom = models.CharField(_('nom de l\'entreprise'), max_length=200)
    slogan = models.CharField(_('slogan'), max_length=200, blank=True)
    logo = models.ImageField(_('logo'), upload_to='company/', blank=True, null=True)
    adresse = models.TextField(_('adresse'), blank=True)
    telephone = models.CharField(_('téléphone'), max_length=50, blank=True)
    email = models.EmailField(_('email'), blank=True)
    site_web = models.URLField(_('site web'), blank=True)
    # Immatriculations
    rccm = models.CharField(_('RCCM'), max_length=50, blank=True, help_text=_('Registre du Commerce et du Crédit Mobilier'))
    id_national = models.CharField(_('ID National / NIF'), max_length=50, blank=True)
    numero_impot = models.CharField(_('Numéro Impôt'), max_length=50, blank=True)
    # Config
    devise = models.CharField(_('devise'), max_length=10, default='FC')
    separateur_milliers = models.CharField(_('séparateur de milliers'), max_length=1, default=' ')
    prefixe_symbole = models.BooleanField(_('symbole avant le montant'), default=True)
    mentions_footer = models.TextField(_('mentions en pied de page'), blank=True, help_text=_('Texte affiché en bas de chaque document PDF'))
    actif = models.BooleanField(_('actif'), default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Entreprise')
        verbose_name_plural = _('Entreprises')
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def format_montant(self, montant):
        """Formate un montant avec la devise configurée."""
        try:
            montant_float = float(montant)
            formatted = f"{montant_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', self.separateur_milliers)
        except (ValueError, TypeError):
            formatted = str(montant)
        prefix = f"{self.devise} " if self.prefixe_symbole else ""
        suffix = f" {self.devise}" if not self.prefixe_symbole else ""
        return f"{prefix}{formatted}{suffix}"


class Category(models.Model):
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to='categories/', blank=True, null=True)
    is_hero = models.BooleanField(_('Afficher en héro'), default=False, 
        help_text=_('Cochez cette case pour mettre cette catégorie en avant dans l\'espace de vente.'))

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


class Supplier(models.Model):
    """Fournisseur pour le réapprovisionnement."""
    nom = models.CharField(_('nom'), max_length=150)
    contact = models.CharField(_('personne de contact'), max_length=150, blank=True)
    email = models.EmailField(_('email'), blank=True)
    telephone = models.CharField(_('téléphone'), max_length=30, blank=True)
    adresse = models.TextField(_('adresse'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    actif = models.BooleanField(_('actif'), default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class ReorderRule(models.Model):
    """Règle de réapprovisionnement automatique pour un produit."""
    produit = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name='reorder_rule',
        verbose_name=_('produit'),
    )
    fournisseur = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='regles', verbose_name=_('fournisseur principal'),
    )
    entrepot = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='regles_reapprovisionnement', verbose_name=_('entrepôt'),
    )
    quantite_min = models.PositiveIntegerField(
        _('stock minimum'), default=10,
        help_text=_('Niveau de stock qui déclenche une alerte.'),
    )
    quantite_cible = models.PositiveIntegerField(
        _('quantité cible'), default=50,
        help_text=_('Quantité à viser après réapprovisionnement.'),
    )
    delai_livraison_jours = models.PositiveIntegerField(
        _('délai de livraison (jours)'), default=7,
        help_text=_('Délai estimé entre la commande et la réception.'),
    )
    actif = models.BooleanField(_('actif'), default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Règle de réapprovisionnement')
        verbose_name_plural = _('Règles de réapprovisionnement')

    def __str__(self):
        return f'{self.produit} → {self.quantite_cible}'

    @property
    def quantite_a_commander(self):
        """Quantité à commander pour atteindre le stock cible."""
        actuel = self.produit.quantite_totale
        if actuel >= self.quantite_cible:
            return 0
        return max(0, self.quantite_cible - actuel)

    @property
    def doit_reapprovisionner(self):
        """Vrai si le stock est sous le minimum."""
        return self.produit.quantite_totale <= self.quantite_min


class PurchaseOrder(models.Model):
    """Bon de commande fournisseur."""
    class Statut(models.TextChoices):
        BROUILLON = 'brouillon', _('Brouillon')
        COMMANDE = 'commande', _('Commandée')
        PARTIELLEMENT_LIVREE = 'partielle', _('Partiellement livrée')
        LIVREE = 'livree', _('Livrée')
        ANNULEE = 'annulee', _('Annulée')

    reference = models.CharField(_('référence'), max_length=50, unique=True, blank=True)
    fournisseur = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='commandes',
        verbose_name=_('fournisseur'),
    )
    entrepot = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, related_name='bons_commande',
        verbose_name=_('entrepôt de destination'),
    )
    statut = models.CharField(
        _('statut'), max_length=20, choices=Statut.choices, default=Statut.BROUILLON,
    )
    date_commande = models.DateField(_('date de commande'), null=True, blank=True)
    date_livraison_prevue = models.DateField(_('livraison prévue'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='bons_commande_crees', verbose_name=_('créée par'),
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Bon de commande')
        verbose_name_plural = _('Bons de commande')
        ordering = ['-cree_le']

    def __str__(self):
        return f'BC {self.reference} — {self.fournisseur}'

    def save(self, *args, **kwargs):
        if not self.reference:
            # Génère une référence automatique
            from django.utils import timezone
            year = timezone.now().year
            count = PurchaseOrder.objects.filter(cree_le__year=year).count() + 1
            self.reference = f'BC-{year}-{count:04d}'
        super().save(*args, **kwargs)

    @property
    def montant_total(self):
        return sum(l.montant_ligne for l in self.lignes.all())


class PurchaseOrderItem(models.Model):
    """Ligne d'un bon de commande fournisseur."""
    bon_commande = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='lignes',
    )
    produit = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='lignes_achat',
    )
    quantite_commandee = models.PositiveIntegerField(_('quantité commandée'), default=1)
    quantite_recue = models.PositiveIntegerField(_('quantité reçue'), default=0)
    prix_unitaire = models.DecimalField(
        _('prix unitaire'), max_digits=10, decimal_places=2, default=0,
    )

    class Meta:
        verbose_name = _('Ligne de bon de commande')
        verbose_name_plural = _('Lignes de bon de commande')

    def __str__(self):
        return f'{self.produit} x{self.quantite_commandee}'

    @property
    def montant_ligne(self):
        return self.quantite_commandee * self.prix_unitaire

    @property
    def est_complete(self):
        return self.quantite_recue >= self.quantite_commandee
