from flask import Flask, render_template, request, redirect, session, flash, jsonify
import os
import json
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'plombiers_hockey_2024_secret_key'

# Configuration
CONFIG = {
    'PASSWORD': "plomberie",
    'DOSSIER_MATCHS': "matchs",
    'ENCODING': 'utf-8'
}

# Base de données des joueurs
JOUEURS_PROFILS = {
    'Simon Djcooleur Tremblay': {
        'nickname': 'DJ la nuit',
        'avatar': '🎧',
        'info': 'Administrateur - Créateur du groupe<br>Enseignant le jour, DJ la nuit',
        'description': 'Enseignant le jour, Simon est un tricératops sur la glace, puissant et agile.',
        'isGoalie': False
    },
    'Hugo Ferland': {
        'nickname': 'Hugo',
        'avatar': '☕',
        'info': 'Travaille chez Café Sobab<br>Membre depuis 1 an environ',
        'description': 'Propriétaire du Sobab, il sert des tasses de café à ses détracteurs. Redoutable en attaque.',
        'isGoalie': False
    },
    'David Rémillard': {
        'nickname': 'Le Journaliste',
        'avatar': '📰',
        'info': 'Journaliste de profession<br>Membre depuis 3 ans environ',
        'description': 'Journaliste de profession, David est connu pour son franc-parler et son tempérament explosif.',
        'isGoalie': False
    },
    'Jean-Dominique Hamel': {
        'nickname': 'JeanDo',
        'avatar': '🤠',
        'info': 'Chansonneur country folk<br>Membre depuis 3 ans environ',
        'description': 'Siffleux en devenir, Jean-Do est un père aimant et artiste de scène.',
        'isGoalie': False
    }
}

def auth_required(f):
    """Décorateur pour les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Accès non autorisé. Veuillez vous connecter.", "error")
            return redirect("/admin")
        return f(*args, **kwargs)
    return decorated_function

class StatsManager:
    """Gestionnaire des statistiques"""
    
    @staticmethod
    def lire_match(date):
        """Lit les données d'un match spécifique"""
        try:
            fichier = os.path.join(CONFIG['DOSSIER_MATCHS'], f"match_{date}.json")
            if os.path.exists(fichier):
                with open(fichier, 'r', encoding=CONFIG['ENCODING']) as f:
                    data = json.load(f)
                    return data if data else {}
            return {}
        except Exception as e:
            print(f"Erreur lecture match {date}: {e}")
            return {}
    
    @staticmethod
    def lister_matches_avec_donnees():
        """Liste tous les matches qui contiennent des données"""
        matches = []
        try:
            if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
                return matches
                
            for fichier in os.listdir(CONFIG['DOSSIER_MATCHS']):
                if fichier.startswith("match_") and fichier.endswith(".json"):
                    date_str = fichier.replace("match_", "").replace(".json", "")
                    data = StatsManager.lire_match(date_str)
                    if data:
                        matches.append(date_str)
            
            return sorted(matches, reverse=True)
        except Exception as e:
            print(f"Erreur listage matches: {e}")
            return []
    
    @staticmethod
    def calculer_classement_general():
        """Calcule le classement général de tous les joueurs"""
        classement = defaultdict(lambda: {
            'buts': 0, 
            'passes': 0, 
            'matchs_joues': 0
        })
        
        try:
            matches = StatsManager.lister_matches_avec_donnees()
            
            for date in matches:
                data = StatsManager.lire_match(date)
                for nom, stats in data.items():
                    nom = nom.strip()
                    if nom:
                        classement[nom]['buts'] += int(stats.get('buts', 0))
                        classement[nom]['passes'] += int(stats.get('passes', 0))
                        classement[nom]['matchs_joues'] += 1
            
            return dict(classement)
        except Exception as e:
            print(f"Erreur calcul classement: {e}")
            return {}
    
    @staticmethod
    def calculer_classement_trie():
        """Retourne le classement trié par points totaux"""
        try:
            stats = StatsManager.calculer_classement_general()
            return sorted(
                stats.items(), 
                key=lambda x: (x[1]['buts'] + x[1]['passes'], x[1]['buts']), 
                reverse=True
            )
        except Exception as e:
            print(f"Erreur tri classement: {e}")
            return []

# Routes principales
@app.route("/")
def accueil():
    """Page d'accueil publique"""
    try:
        classement = StatsManager.calculer_classement_trie()
        
        # Calculer les tops
        stats_general = StatsManager.calculer_classement_general()
        top_buteurs = sorted(stats_general.items(), 
                            key=lambda x: x[1]['buts'], reverse=True)[:3]
        top_passeurs = sorted(stats_general.items(), 
                             key=lambda x: x[1]['passes'], reverse=True)[:3]
        top_points = classement[:3]
        
        return render_template("player.html",
                             classement=classement,
                             top_buteurs=top_buteurs,
                             top_passeurs=top_passeurs,
                             top_points=top_points)
    except Exception as e:
        print(f"Erreur accueil: {e}")
        return f"<h1>Erreur dans l'application</h1><p>{str(e)}</p><a href='/admin'>Admin</a>"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Interface d'administration"""
    try:
        if not session.get("logged_in"):
            if request.method == "POST" and request.form.get("password") == CONFIG['PASSWORD']:
                session["logged_in"] = True
                flash("Connexion réussie !", "success")
                return redirect("/admin")
            elif request.method == "POST":
                flash("Mot de passe incorrect.", "error")
            
            # Page de connexion simple
            return '''
            <html>
            <head><title>Admin - Les Plombiers</title></head>
            <body style="font-family: Arial; max-width: 400px; margin: 100px auto; padding: 20px;">
                <h1>🏒 Admin Les Plombiers</h1>
                <form method="post">
                    <label>Mot de passe:</label><br>
                    <input type="password" name="password" style="width: 100%; padding: 10px; margin: 10px 0;"><br>
                    <button type="submit" style="padding: 10px 20px;">Se connecter</button>
                </form>
                <p><a href="/">← Retour à l'accueil</a></p>
            </body>
            </html>
            '''
        
        # Interface admin simplifiée
        classement = StatsManager.calculer_classement_trie()
        matches = StatsManager.lister_matches_avec_donnees()
        
        html = '''
        <html>
        <head><title>Admin - Les Plombiers</title></head>
        <body style="font-family: Arial; max-width: 800px; margin: 20px auto; padding: 20px;">
            <h1>🏒 Administration Les Plombiers</h1>
            <p><a href="/">← Retour à l'accueil</a> | <a href="/logout">Déconnexion</a></p>
            
            <h2>📊 Classement actuel</h2>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr style="background: #003366; color: white;">
                    <th style="padding: 10px;">Pos</th>
                    <th style="padding: 10px;">Joueur</th>
                    <th style="padding: 10px;">Buts</th>
                    <th style="padding: 10px;">Passes</th>
                    <th style="padding: 10px;">Points</th>
                    <th style="padding: 10px;">Matches</th>
                </tr>
        '''
        
        for i, (nom, stats) in enumerate(classement[:10], 1):
            points = stats['buts'] + stats['passes']
            html += f'''
                <tr style="padding: 8px;">
                    <td style="padding: 8px; text-align: center;"><strong>{i}</strong></td>
                    <td style="padding: 8px;">{nom}</td>
                    <td style="padding: 8px; text-align: center;">{stats['buts']}</td>
                    <td style="padding: 8px; text-align: center;">{stats['passes']}</td>
                    <td style="padding: 8px; text-align: center;"><strong>{points}</strong></td>
                    <td style="padding: 8px; text-align: center;">{stats['matchs_joues']}</td>
                </tr>
            '''
        
        html += '''
            </table>
            
            <h2>📅 Matches enregistrés</h2>
            <ul>
        '''
        
        for match in matches:
            data = StatsManager.lire_match(match)
            total_joueurs = len(data)
            html += f'<li><strong>{match}</strong> - {total_joueurs} joueurs</li>'
        
        html += '''
            </ul>
            
            <h2>🎠 Actions</h2>
            <p><a href="/carousel">Voir le carrousel des joueurs</a></p>
            
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        print(f"Erreur admin: {e}")
        return f"<h1>Erreur admin</h1><p>{str(e)}</p>"

@app.route("/logout")
def logout():
    """Déconnexion"""
    session.pop("logged_in", None)
    flash("Déconnexion réussie", "info")
    return redirect("/")

@app.route("/carousel")
@app.route("/carousel/<nom_joueur>")
def carousel_joueurs(nom_joueur=None):
    """Interface carrousel des joueurs"""
    try:
        stats_general = StatsManager.calculer_classement_general()
        joueurs = list(stats_general.keys())
        
        # Ajouter les joueurs du profil qui ne sont pas encore dans les stats
        for nom in JOUEURS_PROFILS.keys():
            if nom not in joueurs:
                joueurs.append(nom)
        
        if not joueurs:
            return "<h1>Aucun joueur trouvé</h1><p><a href='/'>Retour</a></p>"
        
        # Page simple listant les joueurs
        html = '''
        <html>
        <head><title>Carrousel - Les Plombiers</title></head>
        <body style="font-family: Arial; max-width: 800px; margin: 20px auto; padding: 20px;">
            <h1>🎠 Carrousel des joueurs</h1>
            <p><a href="/">← Retour à l'accueil</a></p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
        '''
        
        for joueur in joueurs:
            profil = JOUEURS_PROFILS.get(joueur, {
                'nickname': '',
                'avatar': '🏒',
                'description': f'{joueur} - Joueur de l\'équipe'
            })
            
            stats = stats_general.get(joueur, {'buts': 0, 'passes': 0, 'matchs_joues': 0})
            points = stats['buts'] + stats['passes']
            
            html += f'''
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; background: white;">
                <div style="text-align: center; font-size: 3em;">{profil.get('avatar', '🏒')}</div>
                <h3>{joueur}</h3>
                <p><em>"{profil.get('nickname', '')}"</em></p>
                <p><strong>Stats saison 2024-25:</strong></p>
                <ul>
                    <li>Buts: {stats['buts']}</li>
                    <li>Passes: {stats['passes']}</li>
                    <li>Points: {points}</li>
                    <li>Matches: {stats['matchs_joues']}</li>
                </ul>
                <p style="font-size: 0.9em; color: #666;">{profil.get('description', '')}</p>
            </div>
            '''
        
        html += '''
            </div>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        print(f"Erreur carrousel: {e}")
        return f"<h1>Erreur carrousel</h1><p>{str(e)}</p><a href='/'>Retour</a>"

@app.errorhandler(404)
def page_not_found(e):
    """Page d'erreur 404"""
    return '''
    <html>
    <head><title>404 - Page non trouvée</title></head>
    <body style="font-family: Arial; text-align: center; padding: 100px;">
        <h1>🏒 404 - Page non trouvée</h1>
        <p>Cette page n'existe pas dans notre arène !</p>
        <a href="/" style="color: #003366;">🏠 Retour à l'accueil</a>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_server_error(e):
    """Page d'erreur 500"""
    return '''
    <html>
    <head><title>500 - Erreur serveur</title></head>
    <body style="font-family: Arial; text-align: center; padding: 100px;">
        <h1>⚠️ 500 - Erreur serveur</h1>
        <p>Quelque chose s'est mal passé sur la glace...</p>
        <a href="/" style="color: #003366;">🏠 Retour à l'accueil</a>
    </body>
    </html>
    ''', 500

if __name__ == "__main__":
    # Créer le dossier matchs s'il n'existe pas
    if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
        os.makedirs(CONFIG['DOSSIER_MATCHS'])
    
    # Configuration pour le déploiement
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print("🏒 Démarrage de l'application Les Plombiers Hockey")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    app.run(debug=debug, host="0.0.0.0", port=port)