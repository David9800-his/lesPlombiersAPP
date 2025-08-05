# Code à ajouter dans agent_stats_hockey.py

import json
import os

# Ajout dans la configuration
CONFIG = {
    'PASSWORD': "plomberie",
    'DOSSIER_MATCHS': "matchs",
    'DOSSIER_PODIUMS': "podiums",  # Nouveau dossier pour les podiums
    'SAISON_DEBUT': datetime(2024, 9, 10),
    'SAISON_FIN': datetime(2025, 4, 29),
    'ENCODING': 'utf-8'
}

class PodiumManager:
    """Gestionnaire des podiums finaux"""
    
    @staticmethod
    def get_podium_file(saison):
        """Retourne le chemin du fichier podium pour une saison"""
        return os.path.join(CONFIG['DOSSIER_PODIUMS'], f"podium_{saison}.json")
    
    @staticmethod
    def save_podium(saison, podium_data):
        """Sauvegarde un podium final"""
        if not os.path.exists(CONFIG['DOSSIER_PODIUMS']):
            os.makedirs(CONFIG['DOSSIER_PODIUMS'])
        
        fichier = PodiumManager.get_podium_file(saison)
        with open(fichier, 'w', encoding=CONFIG['ENCODING']) as f:
            json.dump(podium_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_podium(saison):
        """Charge un podium final"""
        fichier = PodiumManager.get_podium_file(saison)
        try:
            if os.path.exists(fichier):
                with open(fichier, 'r', encoding=CONFIG['ENCODING']) as f:
                    return json.load(f)
            return None
        except (json.JSONDecodeError, Exception):
            return None
    
    @staticmethod
    def get_current_podium():
        """Retourne le podium de la saison actuelle (2024-2025)"""
        return PodiumManager.load_podium("2024-2025")

# Nouvelle route pour gérer les podiums
@app.route("/admin/podium", methods=["POST"])
@auth_required
def admin_podium():
    """Gestion du podium final"""
    try:
        saison = request.form.get("saison_podium")
        statut = request.form.get("statut_saison")
        afficher = "afficher_podium" in request.form
        message = request.form.get("message_podium", "")
        
        # Données du podium
        podium_data = {
            "saison": saison,
            "statut": statut,
            "afficher": afficher,
            "message": message,
            "date_creation": datetime.now().isoformat(),
            "podium": {
                "champion": {
                    "nom": request.form.get("champion_nom"),
                    "buts": int(request.form.get("champion_buts", 0)),
                    "passes": int(request.form.get("champion_passes", 0))
                },
                "second": {
                    "nom": request.form.get("second_nom"),
                    "buts": int(request.form.get("second_buts", 0)),
                    "passes": int(request.form.get("second_passes", 0))
                },
                "third": {
                    "nom": request.form.get("third_nom"),
                    "buts": int(request.form.get("third_buts", 0)),
                    "passes": int(request.form.get("third_passes", 0))
                }
            }
        }
        
        # Sauvegarder
        PodiumManager.save_podium(saison, podium_data)
        
        flash(f"Podium final de la saison {saison} enregistré avec succès!", "success")
        
    except Exception as e:
        flash(f"Erreur lors de la sauvegarde : {str(e)}", "error")
    
    return redirect("/admin")

# Modifier la route d'accueil pour utiliser le podium personnalisé
@app.route("/")
def accueil():
    """Page d'accueil publique - Statistiques pour tous les joueurs"""
    classement = StatsManager.calculer_classement_trie()
    
    # Calculer les tops
    stats_general = StatsManager.calculer_classement_general()
    top_buteurs = sorted(stats_general.items(), 
                        key=lambda x: x[1]['buts'], reverse=True)[:3]
    top_passeurs = sorted(stats_general.items(), 
                         key=lambda x: x[1]['passes'], reverse=True)[:3]
    top_points = classement[:3]
    
    # Charger le podium personnalisé
    podium_final = PodiumManager.get_current_podium()
    
    return render_template("player.html",
                         classement=classement,
                         top_buteurs=top_buteurs,
                         top_passeurs=top_passeurs,
                         top_points=top_points,
                         podium_final=podium_final)

# Modifier la route admin pour inclure la gestion du podium
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
    
    # Charger le podium actuel pour l'affichage dans l'admin
    podium_actuel = PodiumManager.get_current_podium()
    
    return render_template("admin.html",
                         dates=dates_saison,
                         selected_date=selected_date,
                         classement=classement[:10],
                         match_courant=match_courant,
                         podium_actuel=podium_actuel,
                         logged_in=True)

# Route API pour obtenir le podium
@app.route("/api/podium/<saison>")
def api_podium(saison):
    """API pour obtenir le podium d'une saison"""
    podium = PodiumManager.load_podium(saison)
    if podium:
        return jsonify(podium)
    else:
        return jsonify({"error": "Podium non trouvé"}), 404

# Créer le dossier podiums au démarrage
if __name__ == "__main__":
    if not os.path.exists(CONFIG['DOSSIER_MATCHS']):
        os.makedirs(CONFIG['DOSSIER_MATCHS'])
    
    if not os.path.exists(CONFIG['DOSSIER_PODIUMS']):
        os.makedirs(CONFIG['DOSSIER_PODIUMS'])
    
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    app.run(debug=debug, host="0.0.0.0", port=port)