from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from etl.config import DATA_DIR
from etl.db import create_run, finish_run, get_conn, init_schema


EXPECTED_FIELDS = {
    "competition_id",
    "season_id",
    "country_name",
    "competition_name",
    "competition_gender",
    "competition_youth",
    "competition_international",
    "season_name",
    "match_updated",
    "match_updated_360",
    "match_available",
    "match_available_360",
}


@dataclass
class RunResult:
    run_id: int
    row_count: int
    status: str
    error_message: str | None = None


def _parse_ts(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"Invalid timestamp value: {value!r}")
    return datetime.fromisoformat(value)


def extract_competitions(path: Path | None = None) -> list[dict[str, Any]]:
    source = path or (DATA_DIR / "competitions.json")
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("competitions.json must be a JSON array")
    return rows


def transform_competitions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed: list[dict[str, Any]] = []
    for row in rows:
        keys = set(row.keys())
        missing = EXPECTED_FIELDS - keys
        if missing:
            raise ValueError(f"Missing fields in competitions row: {sorted(missing)}")

        transformed.append(
            {
                "competition_id": int(row["competition_id"]),
                "season_id": int(row["season_id"]),
                "country_name": str(row["country_name"]),
                "competition_name": str(row["competition_name"]),
                "competition_gender": (
                    str(row["competition_gender"])
                    if row["competition_gender"] is not None
                    else None
                ),
                "competition_youth": (
                    bool(row["competition_youth"])
                    if row["competition_youth"] is not None
                    else None
                ),
                "competition_international": (
                    bool(row["competition_international"])
                    if row["competition_international"] is not None
                    else None
                ),
                "season_name": str(row["season_name"]),
                "match_updated": _parse_ts(row.get("match_updated")),
                "match_updated_360": _parse_ts(row.get("match_updated_360")),
                "match_available": _parse_ts(row.get("match_available")),
                "match_available_360": _parse_ts(row.get("match_available_360")),
                "raw_payload": json.dumps(row, ensure_ascii=False),
            }
        )
    return transformed


def load_competitions(rows: list[dict[str, Any]]) -> int:
    sql = """
    INSERT INTO competitions (
      competition_id, season_id, country_name, competition_name, competition_gender,
      competition_youth, competition_international, season_name, match_updated,
      match_updated_360, match_available, match_available_360, raw_payload
    )
    VALUES (
      %(competition_id)s, %(season_id)s, %(country_name)s, %(competition_name)s,
      %(competition_gender)s, %(competition_youth)s, %(competition_international)s,
      %(season_name)s, %(match_updated)s, %(match_updated_360)s, %(match_available)s,
      %(match_available_360)s, %(raw_payload)s::jsonb
    )
    ON CONFLICT (competition_id, season_id)
    DO UPDATE SET
      country_name = EXCLUDED.country_name,
      competition_name = EXCLUDED.competition_name,
      competition_gender = EXCLUDED.competition_gender,
      competition_youth = EXCLUDED.competition_youth,
      competition_international = EXCLUDED.competition_international,
      season_name = EXCLUDED.season_name,
      match_updated = EXCLUDED.match_updated,
      match_updated_360 = EXCLUDED.match_updated_360,
      match_available = EXCLUDED.match_available,
      match_available_360 = EXCLUDED.match_available_360,
      raw_payload = EXCLUDED.raw_payload,
      loaded_at = NOW();
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(sql, rows)
        conn.commit()
    return len(rows)


def run_competitions_etl() -> RunResult:
    init_schema()
    run_id = create_run("competitions")
    try:
        extracted = extract_competitions()
        transformed = transform_competitions(extracted)
        row_count = load_competitions(transformed)
        finish_run(run_id=run_id, status="success", row_count=row_count)
        return RunResult(run_id=run_id, row_count=row_count, status="success")
    except Exception as exc:  # noqa: BLE001
        finish_run(run_id=run_id, status="failed", row_count=0, error_message=str(exc))
        return RunResult(
            run_id=run_id, row_count=0, status="failed", error_message=str(exc)
        )
