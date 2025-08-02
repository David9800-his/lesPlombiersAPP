
import mysql.connector
import csv

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="plomberie",
    database="les_plombiers"
)
cursor = conn.cursor()

cursor.execute("SELECT id, prenom, nom, surnom, position, numero, email, telephone, photo_url, actif, date_creation FROM joueurs")
joueurs = cursor.fetchall()
colonnes = [i[0] for i in cursor.description]

with open('joueurs.csv', mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(colonnes)
    writer.writerows(joueurs)

print("Export terminé : joueurs.csv")
cursor.close()
conn.close()
