
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="plomberie"
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS les_plombiers")
cursor.execute("USE les_plombiers")

cursor.execute("DROP TABLE IF EXISTS joueurs")
cursor.execute("""
CREATE TABLE joueurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prenom VARCHAR(50),
    nom VARCHAR(50),
    surnom VARCHAR(50),
    position ENUM('Gardien', 'Défenseur', 'Attaquant') DEFAULT 'Attaquant',
    numero INT DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    telephone VARCHAR(20) DEFAULT NULL,
    photo_url VARCHAR(255) DEFAULT NULL,
    actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

joueurs = [
    ('David', 'Girard'),
    ('Nicolas', 'Savard'),
    ('David', 'Rémillard'),
    ('Simon', 'Kearney'),
    ('Jean-François', 'Breton'),
    ('Simon', 'Tremblay'),
    ('Dave', 'Thériault')
]
cursor.executemany("INSERT INTO joueurs (prenom, nom) VALUES (%s, %s)", joueurs)
conn.commit()
print(f"{cursor.rowcount} joueurs insérés.")

cursor.close()
conn.close()
