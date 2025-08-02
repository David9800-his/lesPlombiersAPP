
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
    j.id AS joueur_id,
    j.prenom,
    j.nom,
    SUM(
        CASE
            WHEN jm.equipe_id = m.equipe_blanc_id AND m.score_blanc > m.score_couleur THEN 1
            WHEN jm.equipe_id = m.equipe_couleur_id AND m.score_couleur > m.score_blanc THEN 1
            ELSE 0
        END
    ) AS victoires,
    SUM(
        CASE
            WHEN jm.equipe_id = m.equipe_blanc_id AND m.score_blanc < m.score_couleur THEN 1
            WHEN jm.equipe_id = m.equipe_couleur_id AND m.score_couleur < m.score_blanc THEN 1
            ELSE 0
        END
    ) AS defaites,
    SUM(
        CASE
            WHEN m.score_blanc = m.score_couleur THEN 1
            ELSE 0
        END
    ) AS nuls
FROM joueurs j
JOIN joueurs_matchs jm ON j.id = jm.joueur_id
JOIN matchs m ON jm.match_id = m.id
GROUP BY j.id
ORDER BY victoires DESC, defaites ASC
""")

resultats = cursor.fetchall()
colonnes = [i[0] for i in cursor.description]

with open('bilan_resultats.csv', mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(colonnes)
    writer.writerows(resultats)

print("Export terminé : bilan_resultats.csv")
cursor.close()
conn.close()
