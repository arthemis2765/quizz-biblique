-- Schéma PostgreSQL pour Bible Quiz.
-- Exécuté automatiquement par db.init_db() au démarrage du serveur.

CREATE TABLE IF NOT EXISTS players (
    pseudo            TEXT PRIMARY KEY,
    current_score     INTEGER NOT NULL DEFAULT 0,
    current_question  INTEGER NOT NULL DEFAULT 0,
    total_questions   INTEGER NOT NULL DEFAULT 0,
    lives             INTEGER NOT NULL DEFAULT 3,
    category          TEXT,
    questions_json    JSONB,
    in_progress        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scores (
    id                SERIAL PRIMARY KEY,
    player_name       TEXT NOT NULL,
    score             INTEGER NOT NULL,
    total_questions   INTEGER NOT NULL,
    category          TEXT,
    lives_used        INTEGER NOT NULL DEFAULT 0,
    played_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scores_player_name ON scores (player_name);
CREATE INDEX IF NOT EXISTS idx_scores_ranking ON scores ((score::float / NULLIF(total_questions, 0)) DESC, score DESC);
