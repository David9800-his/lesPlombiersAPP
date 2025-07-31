
# Agent IA de lecture des stats de hockey avec interface joueur et administrateur

import re
from collections import defaultdict
import csv
import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Requis pour les sessions

# --- Générer les mardis valides ---
def generer_dates_matchs():
    debut = datetime(2024, 9, 10)
    fin = datetime(2025, 4, 29)
    dates = []
    while debut <= fin:
        if debut.weekday() == 1 and not (debut.month == 12 and debut.day in [24, 31]):
            dates.append(debut.strftime('%Y-%m-%d'))
        debut += timedelta(days=1)
    return dates

DATES_MARDIS = generer_dates_matchs()

# --- Exemple de fonction extraire_stats simplifiée ---
def extraire_stats(texte):
    stats = defaultdict(lambda: {"buts": 0, "passes": 0})
    lignes = texte.split("\n")
    for ligne in lignes:
        match = re.match(r"^(.*?)\s+(\d+)\s+buts?\s+(\d+)\s+passes?", ligne)
        if match:
            nom = match.group(1).strip()
            buts = int(match.group(2))
            passes = int(match.group(3))
            stats[nom]["buts"] += buts
            stats[nom]["passes"] += passes
    return stats

# --- Routes ---
@app.route("/historique")
def historique():
    saisons = {
        "2022-2023": [],
        "2023-2024": [],
        "2024-2025": [],
        "2025-2026": []
    }
    for fichier in sorted(os.listdir("matchs")):
        if fichier.startswith("match_") and fichier.endswith(".json"):
            date_str = fichier.replace("match_", "").replace(".json", "")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj >= datetime(2025, 9, 1):
                saisons["2025-2026"].append(date_str)
            elif date_obj >= datetime(2024, 9, 1):
                saisons["2024-2025"].append(date_str)
            elif date_obj >= datetime(2023, 9, 1):
                saisons["2023-2024"].append(date_str)
            else:
                saisons["2022-2023"].append(date_str)

    return render_template("historique.html", saisons=saisons)

@app.route("/telecharger/<date>")
def telecharger_csv(date):
    fichier = f"matchs/match_{date}.json"
    if not os.path.exists(fichier):
        return "Fichier introuvable", 404
    with open(fichier, "r", encoding="utf-8") as f:
        stats = json.load(f)
    lignes = ["Nom,Buts,Passes"]
    for joueur, s in stats.items():
        lignes.append(f"{joueur},{s['buts']},{s['passes']}")
    csv_content = "\n".join(lignes)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=stats_{date}.csv"}
    )

@app.route("/", methods=["GET", "POST"])
def admin():
    commentaires = ""
    error = None
    selected_date = request.form.get("date") or (DATES_MARDIS[0] if DATES_MARDIS else "")

    if request.method == "POST" and not session.get("logged_in"):
        if request.form.get("password") == "Vanier":
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Mot de passe incorrect."

    if not session.get("logged_in"):
        return render_template("admin.html", session=session, commentaires=commentaires, error=error, dates=DATES_MARDIS, selected_date=selected_date)

    if request.method == "POST":
        if request.form.get("reset") == "1":
            for fichier in os.listdir("matchs"):
                if fichier.startswith("match_") and fichier.endswith(".json"):
                    os.remove(os.path.join("matchs", fichier))
            return redirect(url_for("admin"))

        if request.form.get("commentaires"):
            commentaires = request.form["commentaires"]
            stats = extraire_stats(commentaires)
            if not selected_date:
                error = "Veuillez sélectionner une date."
            elif not stats:
                error = "Aucune statistique détectée."
            else:
                with open(f"matchs/match_{selected_date}.json", "w", encoding="utf-8") as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                return redirect(url_for("stats"))

    existing_text = ""
    if selected_date and os.path.exists(f"matchs/match_{selected_date}.json"):
        with open(f"matchs/match_{selected_date}.json", "r", encoding="utf-8") as f:
            existing_text = "\n".join([f"{joueur} : {val['buts']} buts, {val['passes']} passes" for joueur, val in json.load(f).items()])
    commentaires = existing_text if not commentaires else commentaires

    return render_template("admin.html", session=session, commentaires=commentaires, error=error, dates=DATES_MARDIS, selected_date=selected_date)

@app.route("/stats")
def stats():
    cumul = defaultdict(lambda: {"buts": 0, "passes": 0})
    for fichier in os.listdir("matchs"):
        if fichier.startswith("match_") and fichier.endswith(".json"):
            with open(os.path.join("matchs", fichier), "r", encoding="utf-8") as f:
                match_stats = json.load(f)
                for joueur, sp in match_stats.items():
                    cumul[joueur]["buts"] += sp.get("buts", 0)
                    cumul[joueur]["passes"] += sp.get("passes", 0)
    classement = sorted(cumul.items(), key=lambda x: (-x[1]['buts'], -x[1]['passes'], x[0]))
    top_buteurs = sorted(cumul.items(), key=lambda x: -x[1]['buts'])[:3]
    top_passeurs = sorted(cumul.items(), key=lambda x: -x[1]['passes'])[:3]
    top_points = sorted(cumul.items(), key=lambda x: -(x[1]['buts'] + x[1]['passes']))[:3]
    return render_template("player.html",
        classement=classement,
        top_buteurs=top_buteurs,
        top_passeurs=top_passeurs,
        top_points=top_points)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))

# --- Point d'entrée pour Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
