from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator, Optional

import psycopg

from etl.config import get_database_url


@contextmanager
def get_conn() -> Generator[psycopg.Connection, None, None]:
    conn = psycopg.connect(get_database_url())
    try:
        yield conn
    finally:
        conn.close()


def init_schema() -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS competitions (
      competition_id INTEGER NOT NULL,
      season_id INTEGER NOT NULL,
      country_name TEXT NOT NULL,
      competition_name TEXT NOT NULL,
      competition_gender TEXT,
      competition_youth BOOLEAN,
      competition_international BOOLEAN,
      season_name TEXT NOT NULL,
      match_updated TIMESTAMPTZ,
      match_updated_360 TIMESTAMPTZ,
      match_available TIMESTAMPTZ,
      match_available_360 TIMESTAMPTZ,
      raw_payload JSONB NOT NULL,
      loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      PRIMARY KEY (competition_id, season_id)
    );

    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS competition_gender TEXT;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS competition_youth BOOLEAN;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS competition_international BOOLEAN;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS match_updated_360 TIMESTAMPTZ;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS match_available_360 TIMESTAMPTZ;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS raw_payload JSONB;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    CREATE UNIQUE INDEX IF NOT EXISTS competitions_competition_season_uq
      ON competitions (competition_id, season_id);

    CREATE TABLE IF NOT EXISTS etl_runs (
      id BIGSERIAL PRIMARY KEY,
      pipeline_name TEXT NOT NULL,
      status TEXT NOT NULL,
      started_at TIMESTAMPTZ NOT NULL,
      finished_at TIMESTAMPTZ,
      row_count INTEGER DEFAULT 0,
      error_message TEXT
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()


def create_run(pipeline_name: str) -> int:
    started_at = datetime.now(timezone.utc)
    q = """
    INSERT INTO etl_runs (pipeline_name, status, started_at)
    VALUES (%s, 'running', %s)
    RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, (pipeline_name, started_at))
        run_id = cur.fetchone()[0]
        conn.commit()
        return run_id


def finish_run(
    run_id: int,
    status: str,
    row_count: int = 0,
    error_message: Optional[str] = None,
) -> None:
    finished_at = datetime.now(timezone.utc)
    q = """
    UPDATE etl_runs
    SET status = %s,
        finished_at = %s,
        row_count = %s,
        error_message = %s
    WHERE id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, (status, finished_at, row_count, error_message, run_id))
        conn.commit()
