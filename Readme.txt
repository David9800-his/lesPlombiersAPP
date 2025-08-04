# 🏒 Les Plombiers Hockey - Application de Statistiques

Application web complète pour gérer les statistiques de l'équipe de hockey "Les Plombiers".

## 🚀 Fonctionnalités

### 🔧 Interface d'Administration
- **Saisie des statistiques** : Formulaire manuel ou upload CSV
- **Gestion des matches** : Organisation par date (mardis)
- **Historique complet** : Consultation et suppression des matches
- **Export CSV** : Téléchargement des données

### 🎠 Carrousel des Joueurs
- **Profils complets** : 11 joueurs avec descriptions personnalisées
- **Multi-saisons** : Statistiques sur 4 saisons (2022-2025)
- **Navigation fluide** : Flèches, clavier, mode aléatoire
- **URLs personnalisées** : Accès direct à chaque joueur

### 📊 Statistiques Publiques
- **Classement général** : Tri par points, buts, passes
- **Podium interactif** : Top 3 avec animations
- **Tops par catégorie** : Meilleurs buteurs, passeurs, etc.
- **Interface responsive** : Parfait sur tous les appareils

## 🎯 Données Incluses

### Matches d'Avril 2025 (Fin de saison)
- **8 avril** : La soirée légendaire de Jean-Dominique (4 buts)
- **22 avril** : David Rémillard en feu (5 points)
- **29 avril** : Hugo Ferland termine en beauté (4 buts)

### Profils Personnalisés
- **Simon Tremblay** : DJ la nuit, administrateur
- **Nicolas Savard** : Le métalleux amateur de Metallica
- **Jean-François Breton** : Musicien aux plus beaux maillots
- **Hugo Ferland** : Propriétaire du Café Sobab
- **Et 7 autres** avec descriptions complètes

## 🛠️ Installation

### Prérequis
- Python 3.7+
- Flask 2.3.3

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd les-plombiers-hockey
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Intégrer les données de fin de saison**
```bash
python integration_avril.py
```

4. **Lancer l'application**
```bash
python app.py
```

5. **Accéder à l'application**
- Interface admin : http://localhost:5000
- Stats publiques : http://localhost:5000/stats  
- Carrousel : http://localhost:5000/carousel

## 🔐 Authentification

- **Mot de passe admin** : `plomberie`
- **Session sécurisée** : Déconnexion automatique

## 📁 Structure du Projet

```
les-plombiers-hockey/
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances
├── render.yaml              # Configuration Render
├── integration_avril.py     # Script d'intégration
├── templates/               # Templates HTML
│   ├── admin.html          # Interface admin
│   ├── carousel.html       # Carrousel joueurs
│   ├── player.html         # Stats publiques
│   └── historique.html     # Historique matches
├── static/
│   └── style.css          # Styles CSS
└── matchs/                # Données des matches
    ├── match_2025-04-08.json
    ├── match_2025-04-22.json
    └── match_2025-04-29.json
```

## 🌐 Déploiement sur Render

1. **Connecter votre repo** à Render.com
2. **Configuration automatique** via `render.yaml`
3. **Variables d'environnement** : Aucune requise
4. **Déploiement** : Automatique à chaque push

## 📊 API REST

### Endpoints disponibles
- `GET /api/joueurs` - Liste tous les joueurs avec stats
- `GET /carousel/<nom_joueur>` - Accès direct à un joueur
- `GET /telecharger/<date>` - Export CSV d'un match

## 🎮 Navigation

### Raccourcis Clavier (Carrousel)
- **← →** : Navigation entre joueurs
- **Échap** : Fermer les modales

### URLs Amicales
- `/carousel/Hugo%20Ferland` - Fiche de Hugo
- `/carousel/Jean-François%20Breton` - Fiche de JF
- `/carousel/Simon%20Djcooleur%20Tremblay` - Fiche de Simon

## 🎭 Moments Épiques Intégrés

- **Jean-Dominique** : "Que du rêve" + champagne sur Grande Allée
- **David Rémillard** : "On commence à prendre le beat!" (5 points)  
- **Hugo Ferland** : 8 buts en 3 matches de fin de saison
- **Alex Boutin** : De "Nada" à la remontée spectaculaire

## 🔧 Personnalisation

### Ajouter un nouveau joueur
1. Modifier `JOUEURS_PROFILS` dans `app.py`
2. Ajouter avatar, description, informations
3. Redémarrer l'application

### Modifier les saisons
1. Ajuster `CONFIG['SAISON_DEBUT']` et `CONFIG['SAISON_FIN']`
2. Modifier la liste des saisons dans `obtenir_stats_joueur_multi_saisons()`

## 📈 Statistiques Générées

- **Vraies données** : Saison 2025-2026 depuis les fichiers JSON
- **Simulation intelligente** : 3 saisons précédentes avec évolution réaliste
- **Cohérence** : Seed basée sur le nom pour reproduction
- **Évolution** : ±20% de variation par saison

## 🐛 Dépannage

### Problèmes courants
- **Erreur de connexion** : Vérifier le mot de passe "plomberie"
- **Données manquantes** : Exécuter `integration_avril.py`
- **CSS non chargé** : Vérifier le dossier `static/`

### Logs utiles
- Erreurs Flask dans la console
- Messages flash dans l'interface
- Vérification des fichiers JSON dans `matchs/`

## 🤝 Contribution

1. **Fork** le projet
2. **Créer une branche** : `git checkout -b feature/nouvelle-fonctionnalite`
3. **Commit** : `git commit -m 'Ajouter nouvelle fonctionnalité'`
4. **Push** : `git push origin feature/nouvelle-fonctionnalite`
5. **Pull Request** : Créer une PR

## 📄 Licence

Projet développé pour l'équipe Les Plombiers Hockey Vanier.

## 👥 Équipe

- **Développement** : Assistant IA
- **Données** : David Rémillard & Les Plombiers
- **Design** : Interface moderne et responsive

---

**🏒 Que la rondelle soit avec vous ! 🏒**