
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

# [truncated for brevity]
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
