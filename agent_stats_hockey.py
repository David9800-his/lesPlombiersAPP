from flask import Flask, render_template, request, redirect, session, url_for
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'

PASSWORD = "plomberie"
DOSSIER_JSON = "matchs"

# Créer le dossier s'il n'existe pas
if not os.path.exists(DOSSIER_JSON):
    os.makedirs(DOSSIER_JSON)

def generer_dates_mardis():
    debut = datetime(2024, 9, 10)
    fin = datetime(2025, 4, 29)
    dates = []
    while debut <= fin:
        if debut.weekday() == 1:
            dates.append(debut.strftime("%d %B %Y"))
        debut += timedelta(days=1)
    return dates

DATES_MARDIS = generer_dates_mardis()

@app.route('/', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        error = None
        if request.method == 'POST':
            if request.form['password'] == PASSWORD:
                session['logged_in'] = True
                return redirect(url_for('admin'))
            else:
                error = "Mot de passe incorrect"
        return render_template("admin.html", error=error)

    confirmation = None
    error = None
    selected_date = request.form.get("date") or (DATES_MARDIS[0] if DATES_MARDIS else "")
    commentaires = ""

    if request.method == 'POST':
        selected_date = request.form['date']
        commentaires = request.form['commentaires']
        joueurs = []
        for i in range(1, 21):
            nom = request.form.get(f"joueur_{i}")
            buts = request.form.get(f"buts_{i}")
            passes = request.form.get(f"passes_{i}")
            if nom:
                joueurs.append({
                    "nom": nom,
                    "buts": int(buts) if buts else 0,
                    "passes": int(passes) if passes else 0
                })
        if selected_date:
            nom_fichier = os.path.join(DOSSIER_JSON, f"{selected_date}.json")
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                json.dump({"commentaires": commentaires, "joueurs": joueurs}, f, ensure_ascii=False, indent=2)
            confirmation = f"Statistiques enregistrées pour la partie du {selected_date}"

    classement = calculer_classement_general()
    return render_template("admin.html", dates=DATES_MARDIS, selected_date=selected_date, commentaires=commentaires, confirmation=confirmation, classement=classement)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('admin'))

@app.route('/stats')
def stats():
    classement = calculer_classement_general()
    return render_template("player.html", classement=classement)

@app.route('/historique')
def historique():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    fichiers = sorted(os.listdir(DOSSIER_JSON))
    fichiers = [f for f in fichiers if f.endswith('.json')]
    parties = []
    for fichier in fichiers:
        chemin = os.path.join(DOSSIER_JSON, fichier)
        with open(chemin, 'r', encoding='utf-8') as f:
            contenu = json.load(f)
        parties.append({
            "nom": fichier.replace(".json", ""),
            "commentaires": contenu.get("commentaires", "")
        })
    return render_template("historique.html", parties=parties)

@app.route('/supprimer/<nom_partie>')
def supprimer(nom_partie):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    chemin = os.path.join(DOSSIER_JSON, f"{nom_partie}.json")
    if os.path.exists(chemin):
        os.remove(chemin)
    return redirect(url_for('historique'))

def calculer_classement_general():
    stats = defaultdict(lambda: {"buts": 0, "passes": 0})
    fichiers = sorted(os.listdir(DOSSIER_JSON))
    fichiers = [f for f in fichiers if f.endswith('.json')]
    for fichier in fichiers:
        chemin = os.path.join(DOSSIER_JSON, fichier)
        with open(chemin, 'r', encoding='utf-8') as f:
            contenu = json.load(f)
        joueurs = contenu.get("joueurs", [])
        for joueur in joueurs:
            nom = joueur['nom']
            stats[nom]['buts'] += joueur.get('buts', 0)
            stats[nom]['passes'] += joueur.get('passes', 0)
    return sorted(stats.items(), key=lambda item: item[1]['buts'] + item[1]['passes'], reverse=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
