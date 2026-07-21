-- Schéma PostgreSQL pour Bible Quiz Deluxe

-- État courant de chaque joueur (identifié par pseudo).
-- C'est CETTE table qui permet de garder le score quand un joueur
-- se déconnecte et revient : on ne repart jamais de zéro tant que
-- in_progress = TRUE.
CREATE TABLE IF NOT EXISTS players (
    pseudo            TEXT PRIMARY KEY,
    current_score     INTEGER NOT NULL DEFAULT 0,
    current_question  INTEGER NOT NULL DEFAULT 0,
    total_questions   INTEGER NOT NULL DEFAULT 0,
    lives             INTEGER NOT NULL DEFAULT 3,
    category          TEXT NOT NULL DEFAULT 'MIX',
    questions_json     JSONB,              -- questions figées de la partie en cours
    in_progress        BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Historique des parties terminées, utilisé pour le classement.
CREATE TABLE IF NOT EXISTS scores (
    id               SERIAL PRIMARY KEY,
    player_name      TEXT NOT NULL,
    score            INTEGER NOT NULL,
    total_questions  INTEGER NOT NULL,
    category         TEXT NOT NULL DEFAULT 'MIX',
    lives_used       INTEGER NOT NULL DEFAULT 0,
    played_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scores_ranking
    ON scores ((score::float / NULLIF(total_questions, 0)) DESC, score DESC, played_at DESC);
