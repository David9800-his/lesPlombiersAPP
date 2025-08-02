# Les Plombiers - Stats de Hockey 1993

Ce projet est une application web Flask qui affiche les statistiques de hockey d'une ligue locale dans un style rétro inspiré de Netscape Navigator 1993.

## Fonctionnalités

- Page d'accueil publique avec classement dynamique (depuis les CSV de chaque match)
- Interface rétro avec GIFs vintage et style années 90
- Scripts pour exporter les données et générer des rapports

## Structure

- `agent_stats_hockey.py` : Serveur Flask
- `matchs/` : Fichiers CSV par match
- `scripts/` : Utilitaires Python (export, rapport, setup)
- `templates/` : Fichiers HTML
- `static/` : CSS et assets

## Déploiement (Render)

1. Pousser sur GitHub
2. Connecter Render à votre dépôt
3. Utiliser le fichier `render.yaml` pour configuration
