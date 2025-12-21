# 🎓 EpreuvesPro Bénin

<div align="center">
  
  ![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
  ![Django](https://img.shields.io/badge/Django-5.0-green.svg)
  ![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)
  ![License](https://img.shields.io/badge/license-MIT-purple.svg)
  
  **La plateforme n°1 au Bénin pour réussir le BEPC et le BAC** 🇧🇯
  
  [Demo](#) • [Documentation](#) • [Contribuer](#contributing)
  
</div>

---

## 📖 À propos du projet

**EpreuvesPro Bénin** est une plateforme éducative web qui permet aux élèves béninois d'accéder à des milliers d'épreuves et de corrigés détaillés pour les examens du collège et du lycée (BEPC & BAC).

### 🎯 Problème résolu

Au Bénin, les élèves ont difficilement accès à des ressources pédagogiques de qualité pour se préparer aux examens. Les épreuves et corrigés sont souvent :
- Dispersés et difficiles à trouver
- Chers et inaccessibles pour beaucoup
- Non organisés par niveau et matière
- Sans système de paiement mobile adapté

**EpreuvesPro** centralise toutes ces ressources et les rend accessibles à tous, partout, avec paiement mobile intégré.

---

## ✨ Fonctionnalités principales

### Pour les élèves

- 📚 **2500+ épreuves** disponibles (6ème → Terminale)
- ✅ **1800+ corrigés détaillés** avec explications
- 🔍 **Recherche avancée** par classe, matière, période, année
- 💳 **Paiement flexible** : abonnement OU achat à l'unité (25-75 FCFA)
- 📥 **Téléchargements illimités** selon le plan
- 📖 **Bibliothèque de livres** scolaires numériques
- 📊 **Tableau de bord** personnalisé avec statistiques
- 📱 **100% mobile-friendly** pour réviser partout

### Pour les administrateurs

- 🛠️ **Interface admin Django** intuitive
- 📂 **Upload facile** d'épreuves et corrigés PDF
- 💰 **Gestion des paiements** et abonnements
- 📈 **Statistiques détaillées** sur l'utilisation
- 👥 **Gestion des utilisateurs** et leurs accès

---

## 🛠️ Technologies utilisées

### Backend
- **Python 3.11+**
- **Django 5.0** - Framework web
- **SQLite/PostgreSQL** - Base de données
- **Django ORM** - Gestion des données

### Frontend
- **HTML5/CSS3** - Structure et style
- **JavaScript (Vanilla)** - Interactivité
- **Responsive Design** - Compatible tous écrans
- **Google Fonts (Inter)** - Typographie moderne

### Paiement
- **FedaPay API** - Paiements mobiles (Moov, MTN, etc.)
- **Système d'abonnements** personnalisé
- **Achats à l'unité** (épreuves, corrigés, livres)

### Autres
- **Pillow** - Traitement des images
- **Django Forms** - Validation des données
- **Django Messages** - Notifications utilisateur

---

## 📦 Installation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### Étapes d'installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/votre-username/epreuvespro-benin.git
cd epreuvespro-benin
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer le fichier .env avec vos configurations
```

5. **Créer la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Charger les données initiales (optionnel)**
```bash
python manage.py loaddata fixtures/initial_data.json
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

9. **Accéder à l'application**
- Frontend : http://localhost:8000
- Admin : http://localhost:8000/admin

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Django
SECRET_KEY=votre_secret_key_super_securisee
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (Production)
DB_NAME=epreuvespro_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# FedaPay
FEDAPAY_PUBLIC_KEY=pk_sandbox_votre_cle_publique
FEDAPAY_SECRET_KEY=sk_sandbox_votre_cle_secrete
FEDAPAY_MODE=sandbox  # ou 'live' en production
FEDAPAY_WEBHOOK_SECRET=votre_webhook_secret

# URLs
SITE_URL=http://localhost:8000

# Paiements
ACTIVE_PAYMENT_GATEWAY=fedapay
```

### Configuration FedaPay

1. Créer un compte sur [FedaPay](https://fedapay.com)
2. Récupérer vos clés API (sandbox pour test, live pour production)
3. Configurer les webhooks pour recevoir les notifications de paiement
4. URL webhook : `https://votre-domaine.com/paiement/webhook/`

---

## 📁 Structure du projet

```
epreuvespro-benin/
│
├── epreuvespro_benin/          # Configuration principale Django
│   ├── settings.py             # Paramètres du projet
│   ├── urls.py                 # URLs principales
│   └── wsgi.py                 # Configuration WSGI
│
├── core/                       # App pages statiques
│   ├── templates/core/
│   │   ├── accueil.html       # Page d'accueil
│   │   ├── contact.html       # Page contact
│   │   └── about.html         # À propos
│   └── views.py
│
├── accounts/                   # App authentification
│   ├── models.py              # Modèle utilisateur custom
│   ├── views.py               # Connexion, inscription
│   ├── forms.py               # Formulaires auth
│   └── templates/accounts/
│
├── dashboard/                  # App tableau de bord utilisateur
│   ├── views.py               # Vues dashboard
│   ├── templates/dashboard/
│   │   ├── dashboard.html     # Tableau de bord
│   │   ├── parcourir_epreuves.html
│   │   ├── mes_telechargements.html
│   │   └── mon_abonnement.html
│   └── urls.py
│
├── epreuves/                   # App gestion épreuves
│   ├── models.py              # Classe, Matiere, Epreuve, Corrige
│   ├── views.py               # Vues épreuves
│   ├── admin.py               # Interface admin
│   └── templates/epreuves/
│
├── livres/                     # App bibliothèque livres
│   ├── models.py              # CategorieLivre, Livre
│   ├── views.py
│   └── templates/livres/
│
├── abonnements/                # App paiements & abonnements
│   ├── models.py              # PlanAbonnement, Paiement, AchatUnitaire
│   ├── views.py               # Gestion paiements
│   ├── services/
│   │   └── paiement.py        # Intégration FedaPay
│   └── templates/abonnements/
│
├── media/                      # Fichiers uploadés
│   ├── epreuves/              # PDF épreuves
│   ├── corriges/              # PDF corrigés
│   └── livres/                # PDF livres
│
├── static/                     # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                  # Templates globaux
│   └── base.html
│
├── manage.py                   # Script de gestion Django
├── requirements.txt            # Dépendances Python
├── .env.example               # Exemple de variables d'environnement
├── .gitignore                 # Fichiers à ignorer par Git
└── README.md                  # Ce fichier
```

---

## 🚀 Utilisation

### Pour les utilisateurs

1. **S'inscrire** gratuitement sur la plateforme
2. **Choisir un plan** :
   - Gratuit : 3 épreuves offertes
   - Mensuel : 2500 FCFA (100 téléchargements/mois)
   - Annuel : 20000 FCFA (téléchargements illimités)
3. **OU acheter à l'unité** :
   - Épreuve seule : 25 FCFA
   - Corrigé seul : 25 FCFA
   - Pack Épreuve+Corrigé : 50 FCFA
4. **Télécharger** et réviser partout !

### Pour les administrateurs

1. Se connecter à `/admin`
2. Ajouter des classes et matières
3. Uploader des épreuves avec leurs corrigés
4. Gérer les utilisateurs et les paiements
5. Consulter les statistiques

---

## 📊 Tarification

| Plan | Prix | Téléchargements | Corrigés | Support |
|------|------|-----------------|----------|---------|
| 🆓 Gratuit | 0 FCFA | 3 épreuves | ❌ | - |
| 💳 Mensuel | 2500 FCFA/mois | 100/mois | ✅ | Email |
| 💎 Annuel | 20000 FCFA/an | Illimités | ✅ | Prioritaire |

**Achat à l'unité** (sans abonnement) :
- Épreuve : 25 FCFA
- Corrigé : 25 FCFA
- Pack : 50 FCFA
- Livres : 75-500 FCFA

---

## 🎨 Captures d'écran

### Page d'accueil
![Accueil](screenshots/accueil.png)

### Dashboard utilisateur
![Dashboard](screenshots/dashboard.png)

### Parcourir les épreuves
![Epreuves](screenshots/epreuves.png)

### Page de paiement
![Paiement](screenshots/paiement.png)

---

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test epreuves

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
```

---

## 🚀 Déploiement

### Option 1 : Heroku

```bash
# Installer Heroku CLI
heroku login
heroku create epreuvespro-benin

# Configurer PostgreSQL
heroku addons:create heroku-postgresql:mini

# Variables d'environnement
heroku config:set SECRET_KEY=votre_secret_key
heroku config:set DEBUG=False
heroku config:set FEDAPAY_PUBLIC_KEY=pk_live_xxx
heroku config:set FEDAPAY_SECRET_KEY=sk_live_xxx

# Déployer
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 2 : VPS (Ubuntu)

```bash
# Installer les dépendances
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql

# Configurer Gunicorn + Nginx
# Voir documentation complète dans docs/deployment.md
```

---

## 🤝 Contribuer {#contributing}

Les contributions sont les bienvenues ! Voici comment participer :

1. **Fork** le projet
2. **Créer une branche** (`git checkout -b feature/AmazingFeature`)
3. **Commit** les changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir une Pull Request**

### Guidelines

- Suivre les conventions PEP 8 pour Python
- Écrire des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation si nécessaire
- Commenter le code complexe

---

## 🐛 Signaler un bug

Si tu trouves un bug, merci de créer une [issue](https://github.com/votre-username/epreuvespro-benin/issues) avec :
- Description détaillée du problème
- Étapes pour reproduire
- Comportement attendu vs obtenu
- Captures d'écran si pertinent
- Environnement (OS, navigateur, version Python/Django)

---

## 📝 TODO / Roadmap

- [ ] Application mobile (React Native / Flutter)
- [ ] Système de quiz interactifs
- [ ] Forum d'entraide entre élèves
- [ ] Suivi de progression et statistiques avancées
- [ ] Notifications push pour nouveautés
- [ ] Mode révision avec fiches synthétiques
- [ ] Système de parrainage avec récompenses
- [ ] Intégration d'autres moyens de paiement (MTN, Moov)
- [ ] API REST pour intégrations tierces
- [ ] Version desktop (Electron)

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Auteurs

**Votre Nom** - *Développeur principal* - [@votre-github](https://github.com/votre-username)

---

## 🙏 Remerciements

- Merci à tous les professeurs béninois qui partagent leurs ressources
- Merci à la communauté Django pour cet excellent framework
- Merci à FedaPay pour faciliter les paiements mobiles en Afrique
- Merci aux 15 000+ élèves qui utilisent la plateforme

---

## 📞 Contact & Support

- **Email** : contact@epreuvespro.bj
- **WhatsApp** : +229 XX XX XX XX
- **Site web** : https://epreuvespro.bj
- **Facebook** : [@EpreuvesPro](https://facebook.com/epreuvespro)
- **Issues GitHub** : [github.com/votre-username/epreuvespro-benin/issues](https://github.com/votre-username/epreuvespro-benin/issues)

---

## 📈 Statistiques

![GitHub Stars](https://img.shields.io/github/stars/votre-username/epreuvespro-benin?style=social)
![GitHub Forks](https://img.shields.io/github/forks/votre-username/epreuvespro-benin?style=social)
![GitHub Issues](https://img.shields.io/github/issues/votre-username/epreuvespro-benin)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/votre-username/epreuvespro-benin)

---

<div align="center">
  
  **⭐ Si ce projet t'aide, n'hésite pas à lui donner une étoile ! ⭐**
  
  Fait avec ❤️ au Bénin 🇧🇯
  
</div>
