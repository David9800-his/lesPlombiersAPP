
import mysql.connector
import csv

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="plomberie",
    database="les_plombiers"
)
cursor = conn.cursor()

cursor.execute("""
SELECT 
    j.prenom,
    j.nom,
    m.date_match,
    m.lieu,
    s.buts,
    s.passes,
    s.penalites,
    (s.buts + s.passes) AS points
FROM statistiques s
JOIN joueurs j ON s.joueur_id = j.id
JOIN matchs m ON s.match_id = m.id
ORDER BY m.date_match, j.nom
""")

resultats = cursor.fetchall()
colonnes = [i[0] for i in cursor.description]

with open('statistiques_par_match.csv', mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(colonnes)
    writer.writerows(resultats)

print("Export terminé : statistiques_par_match.csv")
cursor.close()
conn.close()
