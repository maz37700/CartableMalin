# 🎒 CartableMalin

Application mobile (web) qui aide les collégiens à ne plus oublier leurs affaires de cours.
Projet pédagogique — Techno 4ᵉ.

## ✨ Ce que fait l'application

- **Saisir son emploi du temps** (jour, heure, matière, salle, prof)
- **Associer le matériel à chaque matière** (cahier rouge, calculatrice, tenue d'EPS…)
- **Calculer automatiquement** la liste des affaires à préparer pour demain
- **Cocher au fur et à mesure** qu'on prépare son sac
- **Voir sa progression** avec barre de pourcentage et stats

## 🛠️ Stack technique

- **Backend** : Python + Flask (un seul fichier `app.py`)
- **Base de données** : SQLite (auto-créée dans `instance/cartable.db`)
- **Frontend** : HTML + CSS + JavaScript vanilla (pas de framework)
- **Design** : Fraunces (titres) + Outfit (corps) + JetBrains Mono (labels)

## 📦 Installation

### 1. Avoir Python 3.8 ou plus

Vérifie avec :
```bash
python --version
```

### 2. Installer Flask

```bash
pip install -r requirements.txt
```

Ou directement :
```bash
pip install Flask
```

### 3. Lancer l'application

```bash
python app.py
```

Ouvre ton navigateur sur **http://localhost:5000**

L'application est calibrée pour ressembler à un téléphone (largeur ~ 460 px).
Pour la voir en taille réelle, ouvre les outils dev (F12) → mode mobile.

## 📁 Structure du projet

```
cartablemalin/
│
├── app.py                  # Backend Flask + routes + base de données
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
│
├── instance/
│   └── cartable.db         # Base SQLite (créée au 1er lancement)
│
├── static/
│   ├── css/
│   │   └── style.css       # Tous les styles
│   └── js/
│       └── app.js          # JavaScript partagé (cocher items)
│
└── templates/
    ├── base.html           # Template parent (topbar + menu)
    ├── accueil.html        # Écran 1 — vue d'ensemble du jour
    ├── cours.html          # Écran 2 — emploi du temps
    ├── sac.html            # Écran 3 — préparer le sac
    ├── materiel.html       # Écran 4 — matériel par matière
    └── profil.html         # Écran 5 — réglages
```

## 🎨 Les 5 écrans

1. **Accueil** : Bonjour + carte coral du jour suivant + liste rapide des affaires à cocher.
2. **Mes cours** : emploi du temps de la semaine, ajout/suppression de cours.
3. **Préparer mon sac** : la grande liste à cocher avec barre de progression et confettis quand tout est prêt.
4. **Mon matériel** : pour chaque matière, ajout/retrait de matériel.
5. **Profil** : prénom, classe, stats, réglages des heures de rappel.

## 💾 Données d'exemple

Au premier lancement, l'application crée automatiquement :
- Un utilisateur "Tom" en 5ᵉC
- Un emploi du temps complet sur 4 jours
- Du matériel pour chaque matière

Tu peux tout modifier ou supprimer ensuite.

## 🚀 Pour aller plus loin

Idées d'amélioration que des élèves de 4ᵉ pourraient explorer :
- Vraies notifications push (avec service worker / PWA)
- Mode sombre
- Export de l'emploi du temps en PDF
- Connexion à Pronote pour récupérer l'emploi du temps automatiquement
- Plusieurs utilisateurs avec compte
- Historique sur plusieurs semaines avec graphiques

---

Made with ❤️ pour le projet techno 4ᵉ
