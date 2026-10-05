"""
Database layer for the AI Trainer multi-agent system.
Stores workout sessions, exercise history, and agent-generated plans.
Uses SQLite for zero-dependency local storage.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "trainer.db"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they don't exist."""
    conn = _get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                started_at  TEXT NOT NULL,
                ended_at    TEXT,
                duration_s  INTEGER,
                session_data TEXT NOT NULL  -- JSON blob of full scorer report
            );

            CREATE TABLE IF NOT EXISTS exercise_sets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES workout_sessions(id),
                exercise    TEXT NOT NULL,
                reps        INTEGER NOT NULL,
                accuracy    REAL NOT NULL,    -- 0-100
                mistakes    TEXT NOT NULL,    -- JSON list of mistake strings
                set_index   INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS agent_reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES workout_sessions(id),
                report_type TEXT NOT NULL,   -- 'session_report' | 'progress_comparison' | 'next_day_plan'
                content     TEXT NOT NULL,   -- full agent-generated text
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS next_day_plans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES workout_sessions(id),
                plan_date   TEXT NOT NULL,   -- date the plan is FOR
                plan_data   TEXT NOT NULL,   -- JSON with exercises, sets, reps targets
                created_at  TEXT NOT NULL
            );
        """)
    conn.close()


def save_session(session_data: Dict[str, Any], started_at: str, ended_at: str) -> int:
    """Persist a completed workout session. Returns the new session ID."""
    conn = _get_connection()
    date_str = datetime.now().strftime("%Y-%m-%d")
    duration_s = None
    try:
        start_dt = datetime.fromisoformat(started_at)
        end_dt = datetime.fromisoformat(ended_at)
        duration_s = int((end_dt - start_dt).total_seconds())
    except Exception:
        pass

    with conn:
        cur = conn.execute(
            "INSERT INTO workout_sessions (date, started_at, ended_at, duration_s, session_data) VALUES (?,?,?,?,?)",
            (date_str, started_at, ended_at, duration_s, json.dumps(session_data)),
        )
        session_id = cur.lastrowid

        for idx, ex in enumerate(session_data.get("exercise_wise_breakdown", [])):
            conn.execute(
                "INSERT INTO exercise_sets (session_id, exercise, reps, accuracy, mistakes, set_index) VALUES (?,?,?,?,?,?)",
                (
                    session_id,
                    ex["exercise"],
                    ex.get("reps", 0),
                    ex.get("accuracy", 0),
                    json.dumps(ex.get("common_mistakes", [])),
                    idx,
                ),
            )
    conn.close()
    return session_id


def save_agent_report(session_id: int, report_type: str, content: str) -> None:
    conn = _get_connection()
    with conn:
        conn.execute(
            "INSERT INTO agent_reports (session_id, report_type, content, created_at) VALUES (?,?,?,?)",
            (session_id, report_type, content, datetime.now().isoformat()),
        )
    conn.close()


def save_next_day_plan(session_id: int, plan_date: str, plan_data: Dict) -> None:
    conn = _get_connection()
    with conn:
        conn.execute(
            "INSERT INTO next_day_plans (session_id, plan_date, plan_data, created_at) VALUES (?,?,?,?)",
            (session_id, plan_date, json.dumps(plan_data), datetime.now().isoformat()),
        )
    conn.close()


def get_last_n_sessions(n: int = 5) -> List[Dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM workout_sessions ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_exercises(session_id: int) -> List[Dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM exercise_sets WHERE session_id=? ORDER BY set_index", (session_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["mistakes"] = json.loads(d["mistakes"])
        result.append(d)
    return result


def get_latest_plan() -> Optional[Dict]:
    """Return the most recently created next-day plan."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM next_day_plans ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    d["plan_data"] = json.loads(d["plan_data"])
    return d


def get_exercise_history(exercise: str, limit: int = 10) -> List[Dict]:
    """Return the last N sets of a specific exercise across all sessions."""
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT es.*, ws.date FROM exercise_sets es
        JOIN workout_sessions ws ON es.session_id = ws.id
        WHERE es.exercise = ? ORDER BY es.id DESC LIMIT ?
        """,
        (exercise, limit),
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["mistakes"] = json.loads(d["mistakes"])
        result.append(d)
    return result
