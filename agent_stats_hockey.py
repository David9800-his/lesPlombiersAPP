from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
import csv
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

PASSWORD = "plomberie"
DOSSIER_MATCHS = "matchs"

# Génère les dates de match du mardi entre deux dates données
def generer_dates_mardi(debut, fin):
    dates = []
    date = debut
    while date <= fin:
        if date.weekday() == 1 and not (date.month == 12 and date.day in [24, 31]):
            dates.append(date.strftime("%Y-%m-%d"))
        date += timedelta(days=1)
    return dates

DATES_MARDIS = generer_dates_mardi(datetime(2024, 9, 10), datetime(2025, 4, 29))

# Classement général calculé dynamiquement
def calculer_classement():
    stats = {}
    for fichier in os.listdir(DOSSIER_MATCHS):
        if fichier.endswith(".json"):
            with open(os.path.join(DOSSIER_MATCHS, fichier), 'r') as f:
                data = json.load(f)
                for joueur, s in data.items():
                    if joueur not in stats:
                        stats[joueur] = {"buts": 0, "passes": 0}
                    stats[joueur]["buts"] += s.get("buts", 0)
                    stats[joueur]["passes"] += s.get("passes", 0)
    # Trier par points
    return sorted(stats.items(), key=lambda x: x[1]['buts'] + x[1]['passes'], reverse=True)

@app.route("/", methods=["GET", "POST"])
def admin():
    error = None
    confirmation = None
    selected_date = request.form.get("date") or (DATES_MARDIS[0] if DATES_MARDIS else "")

    if not session.get("logged_in"):
        if request.method == "POST" and request.form.get("password") == PASSWORD:
            session["logged_in"] = True
        elif request.method == "POST":
            error = "Mot de passe incorrect."
        return render_template("admin.html", error=error, dates=DATES_MARDIS, selected_date=selected_date)

    if request.method == "POST" and 'csv_file' in request.files:
        f = request.files['csv_file']
        if not f:
            error = "Aucun fichier CSV fourni."
        else:
            stats_match = {}
            try:
                contenu = f.read().decode("utf-8").splitlines()
                reader = csv.DictReader(contenu)
                for row in reader:
                    nom = row['Nom'].strip()
                    buts = int(row['Buts'])
                    passes = int(row['Passes'])
                    stats_match[nom] = {"buts": buts, "passes": passes}

                fichier_json = os.path.join(DOSSIER_MATCHS, f"{selected_date}.json")
                with open(fichier_json, 'w') as fout:
                    json.dump(stats_match, fout, indent=2, ensure_ascii=False)

                # Formater la date en format lisible
                date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
                date_formatee = date_obj.strftime("%-d %B %Y")
                confirmation = f"Les statistiques ont été enregistrées pour la partie du {date_formatee}."

            except Exception as e:
                error = f"Erreur lors du traitement du CSV : {str(e)}"

    classement = calculer_classement()
    return render_template("admin.html", error=error, confirmation=confirmation, dates=DATES_MARDIS, selected_date=selected_date, classement=classement)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_MATCHS):
        os.makedirs(DOSSIER_MATCHS)
    port = int(os.environ.get("PORT", 5000))  # Utilise le port de Render, ou 5000 en local
    app.run(debug=True, host="0.0.0.0", port=port)
