"""Accès PostgreSQL pour Bible Quiz ."""

import json
import os

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bible_quiz"
)
if "sslmode" not in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{sep}sslmode=require"

_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)


def _get_conn():
    return _pool.getconn()


def _put_conn(conn):
    _pool.putconn(conn)


def init_db():
    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        schema = f.read()
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()
    finally:
        _put_conn(conn)


# --------------------------------------------------------------------------
# État du joueur (persistance du score entre déconnexions/reconnexions)
# --------------------------------------------------------------------------
def get_player_state(pseudo):
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM players WHERE pseudo = %s", (pseudo,))
            return cur.fetchone()
    finally:
        _put_conn(conn)


def start_or_resume_player(pseudo):
    """Crée le joueur s'il n'existe pas encore, sans jamais écraser une partie en cours."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO players (pseudo)
                VALUES (%s)
                ON CONFLICT (pseudo) DO UPDATE SET updated_at = NOW()
                RETURNING *
                """,
                (pseudo,),
            )
            row = cur.fetchone()
        conn.commit()
        return row
    finally:
        _put_conn(conn)


def begin_new_game(pseudo, questions, category):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE players
                SET current_score = 0,
                    current_question = 0,
                    total_questions = %s,
                    lives = 3,
                    category = %s,
                    questions_json = %s,
                    in_progress = TRUE,
                    updated_at = NOW()
                WHERE pseudo = %s
                """,
                (len(questions), category, json.dumps(questions), pseudo),
            )
        conn.commit()
    finally:
        _put_conn(conn)


def update_progress(pseudo, score, current_question, lives):
    """Sauvegarde l'avancement après CHAQUE question : c'est ce qui rend
    la persistance en temps réel possible (un crash/déco ne perd rien)."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE players
                SET current_score = %s,
                    current_question = %s,
                    lives = %s,
                    updated_at = NOW()
                WHERE pseudo = %s
                """,
                (score, current_question, lives, pseudo),
            )
        conn.commit()
    finally:
        _put_conn(conn)


def end_game(pseudo):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE players
                SET in_progress = FALSE, questions_json = NULL, updated_at = NOW()
                WHERE pseudo = %s
                """,
                (pseudo,),
            )
        conn.commit()
    finally:
        _put_conn(conn)


# --------------------------------------------------------------------------
# Scores / classement
# --------------------------------------------------------------------------
def save_score(player_name, score, total_questions, category, lives_used):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scores (player_name, score, total_questions, category, lives_used)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (player_name, score, total_questions, category, lives_used),
            )
        conn.commit()
    finally:
        _put_conn(conn)


def get_leaderboard(limit=10):
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT name, score, total, cat, date
                FROM (
                    SELECT DISTINCT ON (player_name)
                           player_name AS name, score, total_questions AS total,
                           category AS cat, played_at AS date
                    FROM scores
                    ORDER BY player_name,
                             (score::float / NULLIF(total_questions, 0)) DESC,
                             score DESC, played_at DESC
                ) best_per_player
                ORDER BY (score::float / NULLIF(total, 0)) DESC,
                         score DESC, date DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            for r in rows:
                r["date"] = r["date"].isoformat()
            return rows
    finally:
        _put_conn(conn)


# --------------------------------------------------------------------------
# Répétition espacée (questions ratées par joueur)
# --------------------------------------------------------------------------
def record_answer(player_name, question_id, correct):
    """Met à jour le suivi de répétition espacée pour une question donnée.

    Une réponse fausse augmente wrong_count (la question reviendra plus tôt).
    Deux bonnes réponses d'affilée réinitialisent wrong_count (question « maîtrisée »)."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO wrong_answers (player_name, question_id, wrong_count, correct_streak)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (player_name, question_id) DO UPDATE SET
                    wrong_count = CASE
                        WHEN %s THEN
                            CASE WHEN wrong_answers.correct_streak + 1 >= 2 THEN 0
                                 ELSE wrong_answers.wrong_count END
                        ELSE wrong_answers.wrong_count + 1
                    END,
                    correct_streak = CASE WHEN %s THEN wrong_answers.correct_streak + 1 ELSE 0 END,
                    updated_at = NOW()
                """,
                (player_name, question_id, 0 if correct else 1, 0 if correct else 0,
                 correct, correct),
            )
        conn.commit()
    finally:
        _put_conn(conn)


def get_weak_question_ids(player_name):
    """Retourne les IDs des questions à faire revenir en priorité pour ce joueur
    (déjà ratées et pas encore « maîtrisées »), du plus raté au moins raté."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT question_id FROM wrong_answers
                WHERE player_name = %s AND wrong_count > 0
                ORDER BY wrong_count DESC, updated_at ASC
                """,
                (player_name,),
            )
            return [r["question_id"] for r in cur.fetchall()]
    finally:
        _put_conn(conn)


def get_player_stats(player_name):
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS games,
                    COALESCE(ROUND(AVG(score::float / NULLIF(total_questions, 0)) * 100), 0) AS avg_pct,
                    COALESCE(ROUND(MAX(score::float / NULLIF(total_questions, 0)) * 100), 0) AS best_pct,
                    COALESCE(SUM(score), 0) AS total_score,
                    COALESCE(SUM(total_questions), 0) AS total_questions
                FROM scores
                WHERE player_name = %s
                """,
                (player_name,),
            )
            return cur.fetchone()
    finally:
        _put_conn(conn)
