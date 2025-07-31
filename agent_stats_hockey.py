# Agent IA de lecture des stats de hockey avec interface joueur et administrateur

import re
import os
import json
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --- Générer les mardis valides ---
def generer_dates_matchs():
    debut, fin = datetime(2024, 9, 10), datetime(2025, 4, 29)
    return [debut.strftime('%Y-%m-%d') for debut in (debut + timedelta(days=i) for i in range((fin - debut).days + 1))
            if debut.weekday() == 1 and not (debut.month == 12 and debut.day in [24, 31])]

DATES_MARDIS = generer_dates_matchs()

# --- Extraction des stats ---
def extraire_stats(texte):
    stats = defaultdict(lambda: {"buts": 0, "passes": 0})
    for ligne in texte.split("\n"):
        match = re.match(r"^(.*?)\s+(\d+)\s+buts?\s+(\d+)\s+passes?", ligne)
        if match:
            nom, buts, passes = match.groups()
            stats[nom.strip()]["buts"] += int(buts)
            stats[nom.strip()]["passes"] += int(passes)
    return stats

# --- Routes ---
@app.route("/historique")
def historique():
    saisons = {f"{y}-{y+1}": [] for y in range(2022, 2026)}
    for f in sorted(os.listdir("matchs")):
        if f.startswith("match_") and f.endswith(".json"):
            date_str = f[6:-5]
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                for s in saisons:
                    y1, y2 = map(int, s.split("-"))
                    if datetime(y1, 9, 1) <= date < datetime(y2, 9, 1):
                        saisons[s].append(date_str)
            except: pass
    return render_template("historique.html", saisons=saisons)

@app.route("/telecharger/<date>")
def telecharger_csv(date):
    path = f"matchs/match_{date}.json"
    if not os.path.exists(path): return "Fichier introuvable", 404
    with open(path, "r", encoding="utf-8") as f:
        stats = json.load(f)
    lignes = ["Nom,Buts,Passes"] + [f"{j},{s['buts']},{s['passes']}" for j, s in stats.items()]
    return Response("\n".join(lignes), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename=stats_{date}.csv"})

@app.route("/", methods=["GET", "POST"])
def admin():
    commentaires, error = "", None
    selected_date = request.form.get("date") or (DATES_MARDIS[0] if DATES_MARDIS else "")

    if request.method == "POST" and not session.get("logged_in"):
        if request.form.get("password") == "Vanier":
            session["logged_in"] = True
            return redirect(url_for("admin"))
        error = "Mot de passe incorrect."

    if not session.get("logged_in"):
        return render_template("admin.html", session=session, commentaires=commentaires, error=error,
                               dates=DATES_MARDIS, selected_date=selected_date)

    if request.method == "POST":
        if request.form.get("reset") == "1":
            [os.remove(f"matchs/{f}") for f in os.listdir("matchs") if f.startswith("match_")]
            return redirect(url_for("admin"))

        if request.form.get("commentaires"):
            commentaires = request.form["commentaires"]
            stats = extraire_stats(commentaires)
            if not selected_date:
                error = "Veuillez sélectionner une date."
            elif not stats:
                error = "Aucune statistique détectée."
            else:
                os.makedirs("matchs", exist_ok=True)
                with open(f"matchs/match_{selected_date}.json", "w", encoding="utf-8") as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                return redirect(url_for("stats"))

    path = f"matchs/match_{selected_date}.json"
    if selected_date and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            commentaires = "\n".join([f"{j} : {v['buts']} buts, {v['passes']} passes" for j, v in json.load(f).items()])

    return render_template("admin.html", session=session, commentaires=commentaires, error=error,
                           dates=DATES_MARDIS, selected_date=selected_date)

@app.route("/stats")
def stats():
    cumul = defaultdict(lambda: {"buts": 0, "passes": 0})
    for f in os.listdir("matchs"):
        if f.startswith("match_") and f.endswith(".json"):
            with open(f"matchs/{f}", "r", encoding="utf-8") as fp:
                for joueur, sp in json.load(fp).items():
                    cumul[joueur]["buts"] += sp.get("buts", 0)
                    cumul[joueur]["passes"] += sp.get("passes", 0)
    classement = sorted(cumul.items(), key=lambda x: (-x[1]['buts'], -x[1]['passes'], x[0]))
    return render_template("player.html", classement=classement,
                           top_buteurs=sorted(cumul.items(), key=lambda x: -x[1]['buts'])[:3],
                           top_passeurs=sorted(cumul.items(), key=lambda x: -x[1]['passes'])[:3],
                           top_points=sorted(cumul.items(), key=lambda x: -(x[1]['buts'] + x[1]['passes']))[:3])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
