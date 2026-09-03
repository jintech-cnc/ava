# Ava — Gestion des stocks & inventaires

Outil interne de gestion des stocks : produits, entrepôts, mouvements de stock,
réquisitions internes et commandes clients. Interface fluide et animée grâce à
**HTMX** (mises à jour partielles sans rechargement) et **Alpine.js**
(interactions légères côté client). Multilingue : **Français, English, हिन्दी, 中文**.

## Stack technique

- **Backend** : Django 5 (Python)
- **Frontend** : HTMX 1.9 + Alpine.js 3 + CSS custom (design system maison, sans framework CSS lourd)
- **Base de données** : SQLite (par défaut, migrable vers PostgreSQL plus tard)
- **i18n** : système `django.utils.translation` natif

## Structure du projet

```
ava/
├── config/          # settings, urls racine
├── accounts/        # authentification, profils/rôles
├── inventory/        # catégories, entrepôts, produits, stocks, mouvements
├── orders/           # clients, commandes, réquisitions internes
├── dashboard/         # tableau de bord
├── templates/         # tous les gabarits HTML (dont les partiels HTMX _xxx.html)
├── static/css/style.css
└── locale/            # fichiers de traduction .po/.mo (fr, en, hi, zh-hans)
```

## Installation

```bash
# 1. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 4. Créer un compte administrateur
python manage.py createsuperuser

# 5. Lancer le serveur de développement
python manage.py runserver
```

Rendez-vous sur **http://127.0.0.1:8000/** — vous serez redirigé vers la page
de connexion. Le back-office Django est disponible sur **/admin/** pour
paramétrer rapidement catégories, entrepôts et utilisateurs au démarrage.

## Fonctionnalités incluses

- **Authentification** avec redirection automatique vers le tableau de bord
- **Tableau de bord** : stats en direct (produits, entrepôts, alertes de stock,
  commandes en attente, réquisitions à traiter), animations d'entrée décalées
- **Produits** : liste filtrable/recherchable en HTMX (sans rechargement),
  création/modification en modal, suppression avec confirmation, alerte
  visuelle sous le seuil configuré
- **Mouvements de stock** : entrée / sortie / ajustement / transfert, avec
  mise à jour automatique de la quantité en stock
- **Commandes clients** : formulaire multi-lignes (formset Django) avec calcul
  du sous-total et total
- **Réquisitions internes** : soumission par un employé, workflow
  d'approbation/rejet/livraison réservé au personnel (`is_staff`)
- **Changement de langue** à la volée (FR/EN/HI/ZH) via le sélecteur dans la
  barre latérale, sans perdre la page courante

## Traductions

Les chaînes sont déjà marquées avec `{% trans %}` / `gettext_lazy` dans le
code. Pour générer et compiler les fichiers de traduction (nécessite
`gettext` installé sur le système) :

```bash
python manage.py makemessages -l en -l hi -l zh_Hans
# éditez les fichiers locale/<lang>/LC_MESSAGES/django.po
python manage.py compilemessages
```

Des fichiers `.po` de départ sont déjà fournis dans `locale/` avec quelques
traductions clés ; complétez-les selon vos besoins.

## Prochaines étapes suggérées

- Ajouter des permissions plus fines par rôle (`Profile.role`) au lieu de
  `is_staff` pour les réquisitions
- Brancher un export PDF/Excel des commandes et inventaires
- Ajouter des graphiques (Chart.js) sur le tableau de bord
- Passer sur PostgreSQL en production (changer `DATABASES` dans `config/settings.py`)
- Remplacer `SECRET_KEY` par une variable d'environnement avant mise en production
