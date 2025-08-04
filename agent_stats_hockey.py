from flask import Flask, render_template, request, redirect, session, send_file, flash, jsonify
import os
import json
import csv
from collections import defaultdict
from datetime import datetime, timedelta
import tempfile
from functools import wraps

app = Flask(__name__)
app.secret_key = 'plombiers_hockey_2024_secret_key'

# Configuration
CONFIG = {
    'PASSWORD': "plomberie",
    'DOSSIER_MATCHS': "matchs",
    'SAISON_DEBUT': datetime(2024, 9, 10),
    'SAISON_FIN': datetime(2025, 4, 29),
    'ENCODING': 'utf-8'
}

# Base de données des joueurs avec profils complets
JOUEURS_PROFILS = {
    'Simon Djcooleur Tremblay': {
        'nickname': 'DJ la nuit',
        'avatar': '🎧',
        'info': 'Administrateur - Créateur du groupe<br>Enseignant le jour, DJ la nuit',
        'description': 'Enseignant le jour, Simon est un tricératops sur la glace, puissant et agile. Arrogant avec un sourire éclatant, il dirige la ligue avec charisme. Donnez-lui de l\'espace et il filera à toute vitesse pour décocher un tir du poignet redoutable, laissant ses adversaires médusés.',
        'isGoalie': False
    },
    'Nicolas Savard': {
        'nickname': 'Le Métalleux',
        'avatar': '🤘',
        'info': 'Polyvalente de l\'Ancienne Lorette<br>Membre depuis 3 ans environ',
        'description': 'Nicolas pense que les millénaux et les Gen Z se traînent les pieds, au travail comme sur la glace. Il aime montrer son agilité avec des feintes audacieuses, surtout le toe drag. Amateur de Metallica, il allie puissance et technique pour décrocher des adversaires.',
        'isGoalie': False
    },
    'Jean-François Breton': {
        'nickname': 'JF',
        'avatar': '🎸',
        'info': 'Guitariste/chanteur à BÉNÉVOLE<br>Membre depuis 3 ans environ',
        'description': 'Avec les plus beaux maillots de la ligue, JF s\'est révélé comme une menace offensive. Son gabarit imposant lui assure une présence devant le filet. Musicien populaire, il devra redoubler d\'efforts pour maintenir son niveau de jeu cette saison, malgré une célébrité grandissante.',
        'isGoalie': False
    },
    'Dave Jolicoeur': {
        'nickname': 'L\'Esthète',
        'avatar': '👨‍💼',
        'info': 'Cégep Limoilou<br>Membre depuis 3 ans environ',
        'description': 'Avec un sens esthétique aiguisé, Dave se distingue par sa chevelure et sa moustache impeccable. Photographe de talent, il a l\'œil pour les détails. Sur la glace, son lancer frappe est aussi précis que ses clichés. Mieux vaut éviter son chemin quand il déploie sa puissance.',
        'isGoalie': False
    },
    'Billy Ouellet': {
        'nickname': 'Billy',
        'avatar': '🤫',
        'info': 'Mechanical Technician à Novotex<br>Le mystérieux',
        'description': 'Gardien accompli et insaisissable, Billy est aussi mystérieux qu\'imposant. Sur la glace, il multiplie les arrêts spectaculaires, une mitaine attrapant les tirs les plus dangereux. Hors de la patinoire, il est discret mais surprend avec des blagues grivoises.',
        'isGoalie': True
    },
    'Nicolas Gémus': {
        'nickname': 'Le Papillon',
        'avatar': '🦋',
        'info': 'Polyvalente St-Joseph<br>Membre depuis 3 ans environ',
        'description': 'Maître de l\'art lyrique et gardien au style papillon, Nicolas allie flexibilité et agilité pour frustrer ses adversaires. Sa légendaire coup dése est appréciée autant sur la glace que par sa compagne. Avec ses cuisses solides, il est un rempart infranchissable.',
        'isGoalie': True
    },
    'Simon Kearney': {
        'nickname': 'Le Rockstar',
        'avatar': '🎤',
        'info': 'Détective à FBI<br>Membre depuis 3 ans environ',
        'description': 'Rockstar et inventeur de la pop\'n\'roll, Simon a un coup de patin aussi intense que ses mélodies. Il progresse de saison en saison, visant le top 5 des marqueurs de la ligue sur Billboard. Sa passion pour la musique et le hockey se mêle pour créer une énergie contagieuse.',
        'isGoalie': False
    },
    'David Rémillard': {
        'nickname': 'Le Journaliste',
        'avatar': '📰',
        'info': 'Journaliste de profession<br>Membre depuis 3 ans environ',
        'description': 'Journaliste de profession, David est connu pour son franc-parler et son tempérament explosif. Capable du meilleur comme du pire, il reste une figure marquante sur la glace. Souvent blessé, il brille lorsqu\'il parvient à rester en jeu. David est une source d\'énergie et de passion.',
        'isGoalie': False
    },
    'Jérôme Charette Pépin': {
        'nickname': 'Fantôme Trempette-Chagrin',
        'avatar': '👻',
        'info': 'Membre mystérieux<br>8 amis en commun avec Simon Djcooleur',
        'description': 'Membre énigmatique de l\'équipe, Jérôme navigue entre mystère et performance. Connu sous le pseudonyme de Fantôme Trempette-Chagrin, il apporte une dimension unique au jeu. Ses apparitions sur la glace sont rares mais mémorables.',
        'isGoalie': False
    },
    'Hugo Ferland': {
        'nickname': 'Hugo',
        'avatar': '☕',
        'info': 'Travaille chez Café Sobab<br>Membre depuis 1 an environ',
        'description': 'Souvent comparé à Jimmy, Hugo défend sa propre personnalité unique. Propriétaire du Sobab, il sert des tasses de café à ses détracteurs. Sur la glace, il est redoutable en attaque; les défenseurs doivent toujours l\'avoir à l\'œil. Rapide et imprévisible.',
        'isGoalie': False
    },
    'Jean-Dominique Hamel': {
        'nickname': 'JeanDo',
        'avatar': '🤠',
        'info': 'Chansonneur country folk à JeanDo<br>Membre depuis 3 ans environ',
        'description': 'Siffleux en devenir, Jean-Do est un père aimant et artiste de scène à la tendresse inépuisable. Joueur passionné, il gagnerait à laisser sortir ses émotions hors de la glace pour exploiter pleinement son potentiel. Son tir le remercie d\'avance.',
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
    """Gestionnaire centralisé des statistiques"""
    
    @staticmethod
    def generer_dates_saison():
        """Génère toutes les dates de match de la saison (mardis)"""
        dates = []
        date = CONFIG['SAISON_DEBUT']
        while date <= CONFIG['SAISON_FIN']:
            if date.weekday() == 1 and not (date.month == 12 and date.day in [24, 31]):
                dates.append(date.strftime("%Y-%m-%d"))
            date += timedelta(days=1)
        return dates
    
    @staticmethod
    def lire_match(date):
        """Lit les données d'un match spécifique"""
        fichier = os.path.join(CONFIG['DOSSIER_MATCHS'], f"match_{date}.json")
        try:
            if os.path.exists(fichier):
                with open(fichier, 'r', encoding=CONFIG['ENCODING']) as f:
                    data = json.load(f)
                    return data if data else {}
            return {}
        except (json.JSONDecodeError, Exception):
            return {}
    
    @staticmethod
    def sauvegarder_match(date, stats):
        """Sauvegarde les statistiques d'un match"""
        if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
            os.makedirs(CONFIG['DOSSIER_MATCHS'])
        
        fichier = os.path.join(CONFIG['DOSSIER_MATCHS'], f"match_{date}.json")
        with open(fichier, 'w', encoding=CONFIG['ENCODING']) as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def lister_matches_avec_donnees():
        """Liste tous les matches qui contiennent des données"""
        matches = []
        if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
            return matches
            
        for fichier in os.listdir(CONFIG['DOSSIER_MATCHS']):
            if fichier.startswith("match_") and fichier.endswith(".json"):
                date_str = fichier.replace("match_", "").replace(".json", "")
                data = StatsManager.lire_match(date_str)
                if data:
                    matches.append(date_str)
        
        return sorted(matches, reverse=True)
    
    @staticmethod
    def calculer_classement_general():
        """Calcule le classement général de tous les joueurs"""
        classement = defaultdict(lambda: {
            'buts': 0, 
            'passes': 0, 
            'matchs_joues': 0,
            'derniere_apparition': None
        })
        
        matches = StatsManager.lister_matches_avec_donnees()
        
        for date in matches:
            data = StatsManager.lire_match(date)
            for nom, stats in data.items():
                nom = nom.strip()
                if nom:
                    classement[nom]['buts'] += int(stats.get('buts', 0))
                    classement[nom]['passes'] += int(stats.get('passes', 0))
                    classement[nom]['matchs_joues'] += 1
                    classement[nom]['derniere_apparition'] = date
        
        return dict(classement)
    
    @staticmethod
    def calculer_classement_trie():
        """Retourne le classement trié par points totaux"""
        stats = StatsManager.calculer_classement_general()
        return sorted(
            stats.items(), 
            key=lambda x: (x[1]['buts'] + x[1]['passes'], x[1]['buts']), 
            reverse=True
        )
    
    @staticmethod
    def obtenir_stats_joueur_multi_saisons(nom_joueur):
        """Obtient les statistiques d'un joueur sur plusieurs saisons (simulées)"""
        stats_actuelles = StatsManager.calculer_classement_general().get(nom_joueur, {
            'buts': 0, 'passes': 0, 'matchs_joues': 0
        })
        
        # Simulation des saisons précédentes basée sur les stats actuelles
        import random
        random.seed(hash(nom_joueur))  # Reproduction cohérente
        
        # Profil du joueur
        profil = JOUEURS_PROFILS.get(nom_joueur, {
            'nickname': '',
            'avatar': '🏒',
            'info': f'{nom_joueur}<br>Membre de l\'équipe',
            'description': f'{nom_joueur} est un joueur dévoué qui contribue à l\'équipe avec détermination.',
            'isGoalie': False
        })
        
        saisons = {}
        base_buts = max(stats_actuelles.get('buts', 0), random.randint(5, 25))
        base_passes = max(stats_actuelles.get('passes', 0), random.randint(5, 25))
        base_matches = max(stats_actuelles.get('matchs_joues', 0), random.randint(15, 30))
        
        # Ajustements pour gardiens
        if profil['isGoalie']:
            base_buts = random.randint(0, 3)
            base_passes = random.randint(0, 5)
        
        # Générer les 4 saisons avec évolution
        for i, saison in enumerate(['2025-2026', '2024-2025', '2023-2024', '2022-2023']):
            if i == 0:  # Saison actuelle
                saisons[saison] = {
                    'buts': stats_actuelles.get('buts', base_buts),
                    'passes': stats_actuelles.get('passes', base_passes),
                    'matches': stats_actuelles.get('matchs_joues', base_matches)
                }
            else:
                # Simulation d'évolution avec variations réalistes
                factor = 1 + (random.random() - 0.5) * 0.4  # ±20% variation
                
                # Possibilité qu'un joueur n'était pas là en 2022-2023
                if saison == '2022-2023' and random.random() < 0.3:
                    saisons[saison] = None
                else:
                    saisons[saison] = {
                        'buts': max(0, int(base_buts * factor)),
                        'passes': max(0, int(base_passes * factor)),
                        'matches': max(10, int(base_matches * (0.8 + random.random() * 0.4)))
                    }
        
        return {
            'nom': nom_joueur,
            'profil': profil,
            'saisons': saisons
        }

# Routes principales
@app.route("/")
def accueil():
    """Page d'accueil publique - Statistiques pour tous les joueurs"""
    classement = StatsManager.calculer_classement_trie()
    
    # Calculer les tops
    top_buteurs = sorted(StatsManager.calculer_classement_general().items(), 
                        key=lambda x: x[1]['buts'], reverse=True)[:3]
    top_passeurs = sorted(StatsManager.calculer_classement_general().items(), 
                         key=lambda x: x[1]['passes'], reverse=True)[:3]
    top_points = classement[:3]
    
    return render_template("player.html",
                         classement=classement,
                         top_buteurs=top_buteurs,
                         top_passeurs=top_passeurs,
                         top_points=top_points)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Interface d'administration"""
    dates_saison = StatsManager.generer_dates_saison()
    selected_date = request.form.get("date") or (dates_saison[0] if dates_saison else "")
    
    if not session.get("logged_in"):
        if request.method == "POST" and request.form.get("password") == CONFIG['PASSWORD']:
            session["logged_in"] = True
            flash("Connexion réussie !", "success")
            return redirect("/admin")
        elif request.method == "POST":
            flash("Mot de passe incorrect.", "error")
        
        return render_template("admin.html", 
                             dates=dates_saison, 
                             selected_date=selected_date,
                             logged_in=False)
    
    if request.method == "POST":
        try:
            stats_match = {}
            
            if 'csv_file' in request.files and request.files['csv_file'].filename:
                stats_match = traiter_upload_csv(request.files['csv_file'])
            elif any(request.form.get(f"joueur_{i}") for i in range(1, 21)):
                stats_match = traiter_formulaire_manuel(request.form)
            
            if stats_match:
                StatsManager.sauvegarder_match(selected_date, stats_match)
                date_formatted = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%-d %B %Y")
                flash(f"Statistiques enregistrées pour le {date_formatted} ({len(stats_match)} joueurs)", "success")
            
        except Exception as e:
            flash(f"Erreur lors du traitement : {str(e)}", "error")
    
    classement = StatsManager.calculer_classement_trie()
    match_courant = StatsManager.lire_match(selected_date)
    
    return render_template("admin.html",
                         dates=dates_saison,
                         selected_date=selected_date,
                         classement=classement[:10],
                         match_courant=match_courant,
                         logged_in=True)

def traiter_upload_csv(fichier):
    """Traite l'upload d'un fichier CSV"""
    stats_match = {}
    contenu = fichier.read().decode(CONFIG['ENCODING']).splitlines()
    reader = csv.DictReader(contenu)
    
    for row in reader:
        nom = row.get('Nom', '').strip()
        if nom:
            buts = int(row.get('Buts', 0))
            passes = int(row.get('Passes', 0))
            stats_match[nom] = {"buts": buts, "passes": passes}
    
    return stats_match

def traiter_formulaire_manuel(form_data):
    """Traite les données du formulaire manuel"""
    stats_match = {}
    
    for i in range(1, 21):
        nom = form_data.get(f"joueur_{i}", "").strip()
        if nom:
            buts = int(form_data.get(f"buts_{i}", 0))
            passes = int(form_data.get(f"passes_{i}", 0))
            stats_match[nom] = {"buts": buts, "passes": passes}
    
    return stats_match

@app.route("/logout")
def logout():
    """Déconnexion"""
    session.pop("logged_in", None)
    flash("Déconnexion réussie", "info")
    return redirect("/")

@app.route("/stats")
def stats_publiques():
    """Redirection vers la page d'accueil pour compatibilité"""
    return redirect("/")

@app.route("/carousel")
@app.route("/carousel/<nom_joueur>")
def carousel_joueurs(nom_joueur=None):
    """Interface carrousel des joueurs"""
    tous_joueurs = list(StatsManager.calculer_classement_general().keys())
    
    # Ajouter les joueurs du profil qui ne sont pas encore dans les stats
    for nom in JOUEURS_PROFILS.keys():
        if nom not in tous_joueurs:
            tous_joueurs.append(nom)
    
    # Générer les données pour tous les joueurs
    joueurs_donnees = []
    for nom in tous_joueurs:
        joueurs_donnees.append(StatsManager.obtenir_stats_joueur_multi_saisons(nom))
    
    # Trier par points de la saison actuelle
    joueurs_donnees.sort(key=lambda x: (
        x['saisons']['2025-2026']['buts'] + x['saisons']['2025-2026']['passes'] 
        if x['saisons']['2025-2026'] else 0
    ), reverse=True)
    
    # Index du joueur sélectionné
    index_initial = 0
    if nom_joueur:
        for i, joueur in enumerate(joueurs_donnees):
            if joueur['nom'] == nom_joueur:
                index_initial = i
                break
    
    return render_template("carousel.html", 
                         joueurs=joueurs_donnees,
                         index_initial=index_initial)

@app.route("/api/joueurs")
def api_joueurs():
    """API pour obtenir tous les joueurs avec leurs stats"""
    tous_joueurs = list(StatsManager.calculer_classement_general().keys())
    
    for nom in JOUEURS_PROFILS.keys():
        if nom not in tous_joueurs:
            tous_joueurs.append(nom)
    
    joueurs_donnees = []
    for nom in tous_joueurs:
        joueurs_donnees.append(StatsManager.obtenir_stats_joueur_multi_saisons(nom))
    
    return jsonify(joueurs_donnees)

@app.route("/historique", methods=["GET", "POST"])
@auth_required
def historique():
    """Historique des matches"""
    if request.method == "POST" and request.form.get("supprimer"):
        date_a_supprimer = request.form.get("supprimer")
        fichier_a_supprimer = os.path.join(CONFIG['DOSSIER_MATCHS'], f"match_{date_a_supprimer}.json")
        
        try:
            if os.path.exists(fichier_a_supprimer):
                os.remove(fichier_a_supprimer)
                flash(f"Match du {date_a_supprimer} supprimé avec succès", "success")
            else:
                flash(f"Impossible de supprimer le match du {date_a_supprimer}", "error")
        except Exception as e:
            flash(f"Erreur lors de la suppression : {str(e)}", "error")
    
    # Organiser par saisons
    matches = StatsManager.lister_matches_avec_donnees()
    saisons = defaultdict(list)
    
    for date_str in matches:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj.month >= 9:
                saison = f"{date_obj.year}-{date_obj.year + 1}"
            else:
                saison = f"{date_obj.year - 1}-{date_obj.year}"
            saisons[saison].append(date_str)
        except ValueError:
            continue
    
    for saison in saisons:
        saisons[saison].sort(reverse=True)
    
    return render_template("historique.html", saisons=dict(saisons))

@app.route("/telecharger/<date>")
@auth_required
def telecharger_csv(date):
    """Télécharge les stats d'un match en CSV"""
    data = StatsManager.lire_match(date)
    
    if not data:
        flash("Aucune donnée trouvée pour cette date", "error")
        return redirect("/historique")
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding=CONFIG['ENCODING'])
    
    try:
        writer = csv.writer(temp_file)
        writer.writerow(['Nom', 'Buts', 'Passes', 'Points'])
        
        for nom, stats in data.items():
            buts = stats.get('buts', 0)
            passes = stats.get('passes', 0)
            writer.writerow([nom, buts, passes, buts + passes])
        
        temp_file.close()
        
        return send_file(temp_file.name,
                        as_attachment=True,
                        download_name=f"stats_plombiers_{date}.csv",
                        mimetype='text/csv')
    
    finally:
        try:
            os.unlink(temp_file.name)
        except:
            pass

if __name__ == "__main__":
    if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
        os.makedirs(CONFIG['DOSSIER_MATCHS'])
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)