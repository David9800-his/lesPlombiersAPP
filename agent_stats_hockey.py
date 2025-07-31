from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Vanier"

PASSWORD = "Vanier"

# Liste des mardis entre le 10 septembre et le 29 avril, sauf 24 et 31 décembre
def generer_dates_mardis():
    debut = datetime(2024, 9, 10)
    fin = datetime(2025, 4, 29)
    jours = []
    while debut <= fin:
        if debut.weekday() == 1 and not (debut.month == 12 and debut.day in [24, 31]):
            jours.append(debut.strftime("%Y-%m-%d"))
        debut = debut.replace(day=debut.day + 1)
        try:
            debut = debut.replace(day=debut.day + 1)
        except:
            debut += timedelta(days=1)
    return jours

DATES_MARDIS = generer_dates_mardis()

# Formater une date en format lisible (10 septembre 2024)
def formater_date(date_str):
    mois_fr = {
        "01": "janvier", "02": "février", "03": "mars", "04": "avril",
        "05": "mai", "06": "juin", "07": "juillet", "08": "août",
        "09": "septembre", "10": "octobre", "11": "novembre", "12": "décembre"
    }
    an, mo, jo = date_str.split("-")
    return f"{int(jo)} {mois_fr[mo]} {an}"

# Analyse des commentaires (version simple)
def extraire_stats(texte):
    stats = {}
    lignes = texte.strip().split("\n")
    for ligne in lignes:
        if not ligne.strip():
            continue
        nom = ligne.split(" ")[0]
        buts = ligne.lower().count("but")
        passes = ligne.lower().count("passe")
        if buts > 0 or passes > 0:
            stats[nom] = {"buts": buts, "passes": passes}
    return stats

def enregistrer_stats(date, stats):
    os.makedirs("matchs", exist_ok=True)
    with open(f"matchs/{date}.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def calculer_stats_cumulees():
    classement = {}
    for date in DATES_MARDIS:
        fichier = os.path.join("matchs", f"{date}.json")
        if os.path.exists(fichier):
            with open(fichier, "r", encoding="utf-8") as f:
                stats = json.load(f)
                for joueur, st in stats.items():
                    if joueur not in classement:
                        classement[joueur] = {"buts": 0, "passes": 0}
                    classement[joueur]["buts"] += st.get("buts", 0)
                    classement[joueur]["passes"] += st.get("passes", 0)
    return classement

@app.route("/", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        if request.method == "POST" and request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        return render_template("admin.html", error="" if request.method == "GET" else "Mot de passe incorrect")

    confirmation = None
    error = None
    classement = calculer_stats_cumulees()
    selected_date = request.form.get("date") or (DATES_MARDIS[0] if DATES_MARDIS else "")
    commentaires = ""

    if request.method == "POST" and "commentaires" in request.form:
        commentaires = request.form["commentaires"]
        if commentaires.strip():
            stats = extraire_stats(commentaires)
            enregistrer_stats(selected_date, stats)
            confirmation = f"Les statistiques ont été enregistrées pour la partie du {formater_date(selected_date)}."
        else:
            error = "Aucun commentaire valide détecté."

    return render_template(
        "admin.html",
        dates=DATES_MARDIS,
        commentaires=commentaires,
        selected_date=selected_date,
        confirmation=confirmation,
        error=error,
        classement=classement
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
