from flask import Flask, render_template
import os
import csv
from collections import defaultdict

app = Flask(__name__)
DOSSIER_MATCHS = "matchs"

def calculer_classement_general():
    classement = defaultdict(lambda: {"buts": 0, "passes": 0})
    for nom_fichier in os.listdir(DOSSIER_MATCHS):
        if nom_fichier.endswith(".csv"):
            with open(os.path.join(DOSSIER_MATCHS, nom_fichier), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nom = row.get("Nom", "").strip()
                    prenom = row.get("Prénom", "").strip()
                    if not nom or not prenom:
                        continue
                    joueur = f"{nom},{prenom}"
                    classement[joueur]["buts"] += int(row.get("Buts", 0))
                    classement[joueur]["passes"] += int(row.get("Passes", 0))
    return classement

@app.route("/")
def index():
    classement = calculer_classement_general()
    return render_template("index.html", classement=classement)

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_MATCHS):
        os.makedirs(DOSSIER_MATCHS)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
