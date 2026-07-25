# Déployer Bible Quiz  (PostgreSQL)

## Fichiers du projet
- `app.py` — serveur Flask (routes + questions)
- `db.py` — accès PostgreSQL (scores, classement, stats joueur)
- `schema.sql` — tables créées automatiquement au démarrage
- `index.html` — l'application (servie par Flask)
- `requirements.txt` — dépendances Python
- `Procfile` — commande de lancement pour Render / Railway / Heroku

## 1. Créer une base PostgreSQL
Sur la plupart des hébergeurs (Render, Railway, Supabase, Neon...), tu crées
une base PostgreSQL et tu récupères son `DATABASE_URL` (commence par
`postgresql://...` ou `postgres://...`).

## 2. Configurer la variable d'environnement
Sur ta plateforme, ajoute la variable :
```
DATABASE_URL=postgresql://user:password@host:5432/nom_de_la_base
```
(voir `.env.example` pour le format)

## 3. Déployer
- **Build command** : `pip install -r requirements.txt`
- **Start command** : `gunicorn app:app --bind 0.0.0.0:$PORT` (déjà dans `Procfile`)

Au premier démarrage, `db.init_db()` crée automatiquement les tables
`players` et `scores` à partir de `schema.sql` — aucune migration manuelle
n'est nécessaire.

## 4. Tester en local avant de déployer
```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bible_quiz"
python app.py
```
Puis ouvre `http://localhost:5000`.

## Notes
- `db.py` ajoute automatiquement `sslmode=require` à la connexion dès que
  l'hôte n'est pas `localhost` — utile car la plupart des hébergeurs
  PostgreSQL exigent une connexion chiffrée.
- `bible_trivia.py` (version terminal du jeu) n'est pas utilisé par le site
  web ; il n'a pas besoin d'être déployé.
