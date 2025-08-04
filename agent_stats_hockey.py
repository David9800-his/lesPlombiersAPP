
from flask import Flask, render_template, request, redirect, url_for, session
import os
import csv
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "VanierSecretKey"

DOSSIER_MATCHS = "matchs"

def charger_stats():
    stats = defaultdict(lambda: {'buts': 0, 'passes': 0})
    if not os.path.exists(DOSSIER_MATCHS):
        return stats
    for fichier in os.listdir(DOSSIER_MATCHS):
        if fichier.endswith(".csv"):
            with open(os.path.join(DOSSIER_MATCHS, fichier), newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nom = row["Nom"]
                    prenom = row["Prénom"]
                    cle = f"{prenom} {nom}"
                    stats[cle]["buts"] += int(row.get("Buts", 0))
                    stats[cle]["passes"] += int(row.get("Passes", 0))
    return stats

@app.route("/")
def accueil():
    classement = sorted(charger_stats().items(), key=lambda x: x[1]['buts'] + x[1]['passes'], reverse=True)
    return render_template("player.html", classement=classement)

@app.route("/carousel")
def carousel():
    return render_template("carousel.html")

@app.route("/fiche")
def fiche_joueur():
    return render_template("fiche_joueur.html")

@app.route("/historique")
def historique():
    return render_template("historique.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == "Vanier":
            session["logged_in"] = True
        return redirect(url_for("admin"))
    if not session.get("logged_in"):
        return render_template("login.html")
    return redirect(url_for("accueil"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("accueil"))

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_MATCHS):
        os.makedirs(DOSSIER_MATCHS)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
