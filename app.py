"""
CartableMalin — Application Flask
Aide les collégiens à ne plus oublier leurs affaires de cours.
Projet techno 4ᵉ — exemple pédagogique
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)

# ===================================================================
# BASE DE DONNÉES
# ===================================================================
DB_PATH = os.path.join(app.instance_path, 'cartable.db')

def get_db():
    """Connexion à la base de données SQLite."""
    os.makedirs(app.instance_path, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base avec les tables nécessaires."""
    conn = get_db()
    c = conn.cursor()

    # Table USER : un seul utilisateur par installation
    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            prenom TEXT DEFAULT 'Tom',
            classe TEXT DEFAULT '5ᵉC',
            college TEXT DEFAULT 'Collège Picasso',
            heure_rappel_soir TEXT DEFAULT '19:00',
            heure_rappel_matin TEXT DEFAULT '07:30'
        )
    ''')

    # Table COURS : chaque ligne = un cours dans l'emploi du temps
    c.execute('''
        CREATE TABLE IF NOT EXISTS cours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jour INTEGER NOT NULL,
            heure TEXT NOT NULL,
            matiere TEXT NOT NULL,
            salle TEXT,
            prof TEXT
        )
    ''')

    # Table MATERIEL : matériel à associer à chaque matière
    c.execute('''
        CREATE TABLE IF NOT EXISTS materiel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere TEXT NOT NULL,
            nom TEXT NOT NULL,
            icone TEXT DEFAULT '📚'
        )
    ''')

    # Table CHECK_DAY : ce qui est coché aujourd'hui
    c.execute('''
        CREATE TABLE IF NOT EXISTS check_day (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_iso TEXT NOT NULL,
            materiel_nom TEXT NOT NULL,
            coche INTEGER DEFAULT 0,
            UNIQUE(date_iso, materiel_nom)
        )
    ''')

    # Table HISTORIQUE : pour le suivi (combien de jours réussis, oublis…)
    c.execute('''
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_iso TEXT NOT NULL UNIQUE,
            taux_reussite INTEGER,
            total_items INTEGER,
            items_coches INTEGER
        )
    ''')

    # Insère un utilisateur par défaut s'il n'existe pas
    c.execute("SELECT COUNT(*) FROM user")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO user (prenom, classe, college) VALUES ('Tom', '5ᵉC', 'Collège Picasso')")
        # Insert de données d'exemple : un emploi du temps de mardi
        cours_demo = [
            (1, '08:00', 'Maths', 'Salle 12', 'M. Durand'),
            (1, '09:00', 'Anglais', 'Salle 8', 'Mme Smith'),
            (1, '10:00', 'EPS', 'Gymnase', 'Mme Roux'),
            (1, '11:00', 'SVT', 'Salle 23', 'M. Patel'),
            (1, '14:00', 'Français', 'Salle 5', 'Mme Léon'),
            (1, '15:00', 'Histoire-Géo', 'Salle 17', 'M. Garcia'),
            (2, '08:00', 'Français', 'Salle 5', 'Mme Léon'),
            (2, '09:00', 'Maths', 'Salle 12', 'M. Durand'),
            (2, '10:00', 'Arts plastiques', 'Salle 21', 'Mme Bouchet'),
            (2, '14:00', 'Techno', 'Salle techno', 'M. Maz'),
            (2, '15:00', 'Techno', 'Salle techno', 'M. Maz'),
            (3, '08:00', 'EPS', 'Gymnase', 'Mme Roux'),
            (3, '09:00', 'EPS', 'Gymnase', 'Mme Roux'),
            (3, '10:00', 'Anglais', 'Salle 8', 'Mme Smith'),
            (3, '11:00', 'Maths', 'Salle 12', 'M. Durand'),
            (4, '08:00', 'SVT', 'Salle 23', 'M. Patel'),
            (4, '09:00', 'Histoire-Géo', 'Salle 17', 'M. Garcia'),
            (4, '10:00', 'Français', 'Salle 5', 'Mme Léon'),
            (4, '14:00', 'Maths', 'Salle 12', 'M. Durand'),
            (4, '15:00', 'Musique', 'Salle 14', 'Mme Lemaire'),
        ]
        c.executemany(
            "INSERT INTO cours (jour, heure, matiere, salle, prof) VALUES (?, ?, ?, ?, ?)",
            cours_demo
        )

        # Matériel par défaut associé à chaque matière
        materiel_demo = [
            ('Maths', 'Cahier de maths', '📕'),
            ('Maths', 'Calculatrice', '🧮'),
            ('Maths', 'Manuel de maths', '📖'),
            ('Anglais', 'Cahier d\'anglais', '📓'),
            ('Anglais', 'Manuel d\'anglais', '📖'),
            ('Français', 'Cahier de français', '📔'),
            ('Français', 'Livre de lecture', '📙'),
            ('SVT', 'Cahier de SVT', '📗'),
            ('SVT', 'Manuel de SVT', '📖'),
            ('Histoire-Géo', 'Cahier d\'Histoire-Géo', '📘'),
            ('Histoire-Géo', 'Atlas', '🗺️'),
            ('EPS', 'Tenue d\'EPS', '👕'),
            ('EPS', 'Baskets', '👟'),
            ('EPS', 'Bouteille d\'eau', '💧'),
            ('Arts plastiques', 'Crayons de couleur', '🖍️'),
            ('Arts plastiques', 'Pinceaux', '🖌️'),
            ('Arts plastiques', 'Cahier d\'arts', '🎨'),
            ('Techno', 'Classeur de techno', '🗂️'),
            ('Techno', 'Stylos', '🖊️'),
            ('Musique', 'Flûte', '🎵'),
            ('Musique', 'Cahier de musique', '📓'),
        ]
        c.executemany(
            "INSERT INTO materiel (matiere, nom, icone) VALUES (?, ?, ?)",
            materiel_demo
        )

    conn.commit()
    conn.close()

# ===================================================================
# HELPERS
# ===================================================================
def get_user():
    """Retourne le premier utilisateur (un seul utilisateur par installation)."""
    conn = get_db()
    user = conn.execute("SELECT * FROM user LIMIT 1").fetchone()
    conn.close()
    return dict(user) if user else None

def get_demain_index():
    """Retourne l'index du jour de DEMAIN (lundi=0, mardi=1, …, vendredi=4).
    Si demain est samedi/dimanche, retourne le lundi suivant."""
    today = date.today()
    # weekday: lundi=0, dimanche=6
    demain = today + timedelta(days=1)
    if demain.weekday() >= 5:  # week-end
        # On cherche le prochain lundi
        days_until_monday = (7 - demain.weekday()) % 7
        demain = demain + timedelta(days=days_until_monday)
    return demain

JOURS_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
MOIS_FR  = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

def get_materiel_demain():
    """Calcule la liste UNIQUE de matériel à apporter pour demain."""
    demain = get_demain_index()
    jour_idx = demain.weekday()  # 0=lundi … 4=vendredi

    conn = get_db()
    # Matières du jour de demain
    cours = conn.execute(
        "SELECT DISTINCT matiere FROM cours WHERE jour = ?", (jour_idx,)
    ).fetchall()
    matieres = [c['matiere'] for c in cours]

    if not matieres:
        conn.close()
        return [], demain

    # Matériel uniques (un même cahier peut servir à 2 cours)
    placeholders = ','.join(['?'] * len(matieres))
    materiel = conn.execute(
        f"SELECT DISTINCT nom, icone, matiere FROM materiel WHERE matiere IN ({placeholders}) ORDER BY matiere, nom",
        matieres
    ).fetchall()

    items = []
    seen = set()
    for m in materiel:
        if m['nom'] not in seen:
            seen.add(m['nom'])
            items.append(dict(m))

    # Récupère l'état coché du jour
    date_iso = demain.isoformat()
    cocher_rows = conn.execute(
        "SELECT materiel_nom, coche FROM check_day WHERE date_iso = ?", (date_iso,)
    ).fetchall()
    coches = {r['materiel_nom']: r['coche'] for r in cocher_rows}

    for it in items:
        it['coche'] = coches.get(it['nom'], 0) == 1

    conn.close()
    return items, demain

def get_stats():
    """Stats simples : nb jours suivis, taux moyen, oublis."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM historique ORDER BY date_iso DESC LIMIT 30").fetchall()
    conn.close()

    if not rows:
        return {'jours_suivis': 0, 'taux_moyen': 0, 'oublis': 0}

    jours_suivis = len(rows)
    taux_moyen = round(sum(r['taux_reussite'] for r in rows) / jours_suivis)
    oublis = sum(1 for r in rows if r['taux_reussite'] < 100)
    return {'jours_suivis': jours_suivis, 'taux_moyen': taux_moyen, 'oublis': oublis}

# ===================================================================
# ROUTES
# ===================================================================

@app.route('/')
def accueil():
    """Écran 1 : Accueil — vue d'ensemble du jour."""
    user = get_user()
    items, demain = get_materiel_demain()

    nb_total = len(items)
    nb_coches = sum(1 for i in items if i['coche'])

    contexte = {
        'user': user,
        'items': items,
        'date_demain_str': f"{JOURS_FR[demain.weekday()].upper()} {demain.day} {MOIS_FR[demain.month].upper()}",
        'jour_demain': JOURS_FR[demain.weekday()],
        'nb_total': nb_total,
        'nb_coches': nb_coches,
        'progression': round((nb_coches / nb_total * 100) if nb_total else 0)
    }
    return render_template('accueil.html', **contexte)


@app.route('/cours')
def cours():
    """Écran 2 : Emploi du temps."""
    user = get_user()
    conn = get_db()
    cours = conn.execute("SELECT * FROM cours ORDER BY jour, heure").fetchall()
    conn.close()

    # Organise par jour
    semaine = {i: [] for i in range(5)}
    for c in cours:
        semaine[c['jour']].append(dict(c))

    # Date de chaque jour de la semaine en cours
    today = date.today()
    debut_semaine = today - timedelta(days=today.weekday())
    dates_semaine = [debut_semaine + timedelta(days=i) for i in range(5)]

    return render_template('cours.html',
        user=user,
        semaine=semaine,
        dates_semaine=dates_semaine,
        jours_fr=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'],
        jour_actuel=today.weekday() if today.weekday() < 5 else 0)


@app.route('/cours/ajouter', methods=['POST'])
def ajouter_cours():
    """Ajouter un cours à l'emploi du temps."""
    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO cours (jour, heure, matiere, salle, prof) VALUES (?, ?, ?, ?, ?)",
        (data['jour'], data['heure'], data['matiere'], data.get('salle', ''), data.get('prof', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/cours/supprimer/<int:cours_id>', methods=['DELETE'])
def supprimer_cours(cours_id):
    conn = get_db()
    conn.execute("DELETE FROM cours WHERE id = ?", (cours_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/sac')
def sac():
    """Écran 3 : Liste à cocher pour préparer le sac."""
    user = get_user()
    items, demain = get_materiel_demain()
    nb_total = len(items)
    nb_coches = sum(1 for i in items if i['coche'])

    return render_template('sac.html',
        user=user,
        items=items,
        date_demain_str=f"Demain · {JOURS_FR[demain.weekday()]} {demain.day} {MOIS_FR[demain.month]}",
        jour_demain=JOURS_FR[demain.weekday()],
        nb_total=nb_total,
        nb_coches=nb_coches,
        progression=round((nb_coches / nb_total * 100) if nb_total else 0))


@app.route('/sac/cocher', methods=['POST'])
def cocher():
    """Coche/décoche un item."""
    data = request.json
    demain = get_demain_index()
    date_iso = demain.isoformat()

    conn = get_db()
    # Insert ou update
    conn.execute('''
        INSERT INTO check_day (date_iso, materiel_nom, coche) VALUES (?, ?, ?)
        ON CONFLICT(date_iso, materiel_nom) DO UPDATE SET coche = excluded.coche
    ''', (date_iso, data['nom'], 1 if data['coche'] else 0))

    # Met à jour l'historique
    items, _ = get_materiel_demain()
    nb_total = len(items)
    nb_coches = sum(1 for i in items if i['coche'])
    if nb_total > 0:
        taux = round(nb_coches / nb_total * 100)
        conn.execute('''
            INSERT INTO historique (date_iso, taux_reussite, total_items, items_coches)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date_iso) DO UPDATE SET
                taux_reussite = excluded.taux_reussite,
                total_items = excluded.total_items,
                items_coches = excluded.items_coches
        ''', (date_iso, taux, nb_total, nb_coches))

    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'progression': round((nb_coches / nb_total * 100) if nb_total else 0)})


@app.route('/profil', methods=['GET', 'POST'])
def profil():
    """Écran 5 : Profil et réglages."""
    if request.method == 'POST':
        data = request.json
        conn = get_db()
        conn.execute('''
            UPDATE user SET prenom = ?, classe = ?, college = ?,
            heure_rappel_soir = ?, heure_rappel_matin = ?
            WHERE id = (SELECT id FROM user LIMIT 1)
        ''', (data['prenom'], data['classe'], data['college'],
              data['heure_rappel_soir'], data['heure_rappel_matin']))
        conn.commit()
        conn.close()
        return jsonify({'ok': True})

    user = get_user()
    stats = get_stats()
    return render_template('profil.html', user=user, stats=stats)


@app.route('/materiel')
def materiel_page():
    """Écran 4 : Gestion du matériel par matière."""
    user = get_user()
    conn = get_db()
    matieres_rows = conn.execute("SELECT DISTINCT matiere FROM cours ORDER BY matiere").fetchall()
    matieres = [m['matiere'] for m in matieres_rows]

    materiel_par_matiere = {}
    for mat in matieres:
        items = conn.execute(
            "SELECT * FROM materiel WHERE matiere = ? ORDER BY nom", (mat,)
        ).fetchall()
        materiel_par_matiere[mat] = [dict(i) for i in items]

    conn.close()
    return render_template('materiel.html',
        user=user,
        materiel_par_matiere=materiel_par_matiere,
        matieres=matieres)


@app.route('/materiel/ajouter', methods=['POST'])
def ajouter_materiel():
    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO materiel (matiere, nom, icone) VALUES (?, ?, ?)",
        (data['matiere'], data['nom'], data.get('icone', '📚'))
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/materiel/supprimer/<int:materiel_id>', methods=['DELETE'])
def supprimer_materiel(materiel_id):
    conn = get_db()
    conn.execute("DELETE FROM materiel WHERE id = ?", (materiel_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ===================================================================
# INITIALISATION DE LA BDD AU DÉMARRAGE DU MODULE
# (Important pour Render et autres hébergeurs : init_db doit être
#  appelé même quand l'app est lancée par Gunicorn et pas directement)
# ===================================================================
init_db()


# ===================================================================
# LANCEMENT EN LOCAL
# ===================================================================
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🎒  CartableMalin — Serveur démarré")
    print("=" * 60)
    print(f"Ouvre ton navigateur sur :  http://localhost:{port}")
    print("Appuie sur Ctrl+C pour arrêter.")
    print("=" * 60)
    app.run(debug=True, port=port, host='0.0.0.0')
