from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from etl.competitions_etl import run_competitions_etl
from etl.db import get_conn, init_schema

app = Flask(__name__)


INDEX_TEMPLATE = """
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>ETL Monitor - Competitions</title>
    <style>
      :root {
        --bg: #f2f7fb;
        --card: #ffffff;
        --ink: #13293d;
        --line: #d8e1e8;
        --accent: #005f73;
        --accent-hover: #0a7b92;
        --ok: #0a7f2e;
        --ko: #9b2226;
      }
      body {
        font-family: "Avenir Next", "Segoe UI", Arial, sans-serif;
        margin: 0;
        color: var(--ink);
        background: radial-gradient(circle at top right, #e2eef6 0%, var(--bg) 45%);
      }
      .wrap { max-width: 1180px; margin: 1.5rem auto; padding: 0 1rem; }
      .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
      }
      h1, h2, h3 { margin-top: 0; }
      .meta { color: #3f5f7a; font-size: .95rem; margin-bottom: 1rem; }
      .actions { display: flex; gap: .75rem; align-items: center; flex-wrap: wrap; }
      button {
        background: var(--accent);
        color: #fff;
        border: none;
        padding: .65rem 1rem;
        border-radius: 8px;
        cursor: pointer;
      }
      button:hover { background: var(--accent-hover); }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .8rem; }
      .stat { border: 1px solid var(--line); border-radius: 10px; padding: .8rem; background: #fbfdff; }
      .stat .k { font-size: .85rem; color: #5b778f; }
      .stat .v { font-size: 1.4rem; font-weight: 700; margin-top: .2rem; }
      table { border-collapse: collapse; width: 100%; margin-top: .7rem; font-size: .95rem; }
      th, td { border: 1px solid var(--line); padding: .48rem; text-align: left; vertical-align: top; }
      th { background: #f7fbff; }
      .ok { color: var(--ok); font-weight: 700; }
      .ko { color: var(--ko); font-weight: 700; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: .88rem; }
      .err { white-space: pre-wrap; max-width: 480px; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="card">
        <h1>Suivi ETL - Competitions</h1>
        <p class="meta">URL de suivi: <code>{{ base_url }}</code></p>
        <div class="actions">
          <form method="post" action="{{ url_for('run_competitions') }}">
            <button type="submit">Lancer ETL competitions</button>
          </form>
          <a href="{{ url_for('runs_api') }}" class="mono">{{ base_url }}/api/runs</a>
        </div>
      </div>

      <div class="card">
        <h2>Synthèse</h2>
        <div class="grid">
          <div class="stat"><div class="k">Lignes competitions</div><div class="v">{{ summary.total_competitions }}</div></div>
          <div class="stat"><div class="k">Runs totaux</div><div class="v">{{ summary.total_runs }}</div></div>
          <div class="stat"><div class="k">Runs success</div><div class="v">{{ summary.success_runs }}</div></div>
          <div class="stat"><div class="k">Runs failed</div><div class="v">{{ summary.failed_runs }}</div></div>
          <div class="stat"><div class="k">Dernier run id</div><div class="v">{{ latest.id if latest else "-" }}</div></div>
          <div class="stat"><div class="k">Durée dernier run</div><div class="v">{{ latest.duration_seconds if latest and latest.duration_seconds is not none else "-" }}s</div></div>
        </div>
      </div>

      <div class="card">
        <h2>Derniers runs (20)</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Pipeline</th>
              <th>Status</th>
              <th>Rows</th>
              <th>Durée(s)</th>
              <th>Started</th>
              <th>Finished</th>
              <th>Erreur</th>
            </tr>
          </thead>
          <tbody>
            {% for run in runs %}
              <tr>
                <td>{{ run.id }}</td>
                <td>{{ run.pipeline_name }}</td>
                <td class="{{ 'ok' if run.status == 'success' else 'ko' if run.status == 'failed' else '' }}">{{ run.status }}</td>
                <td>{{ run.row_count }}</td>
                <td>{{ run.duration_seconds if run.duration_seconds is not none else '' }}</td>
                <td class="mono">{{ run.started_at }}</td>
                <td class="mono">{{ run.finished_at or '' }}</td>
                <td class="err">{{ run.error_message or '' }}</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>Erreurs récentes (5)</h2>
        <table>
          <thead>
            <tr><th>Run ID</th><th>Date</th><th>Erreur</th></tr>
          </thead>
          <tbody>
            {% for err in recent_errors %}
              <tr>
                <td>{{ err.id }}</td>
                <td class="mono">{{ err.started_at }}</td>
                <td class="err">{{ err.error_message }}</td>
              </tr>
            {% else %}
              <tr><td colspan="3">Aucune erreur récente</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>Aperçu competitions (15)</h2>
        <table>
          <thead>
            <tr>
              <th>Competition ID</th>
              <th>Season ID</th>
              <th>Pays</th>
              <th>Compétition</th>
              <th>Saison</th>
              <th>Maj match</th>
            </tr>
          </thead>
          <tbody>
            {% for comp in competitions_preview %}
              <tr>
                <td>{{ comp.competition_id }}</td>
                <td>{{ comp.season_id }}</td>
                <td>{{ comp.country_name }}</td>
                <td>{{ comp.competition_name }}</td>
                <td>{{ comp.season_name }}</td>
                <td class="mono">{{ comp.match_updated or '' }}</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </body>
</html>
"""


def _fetch_dashboard_data() -> dict:
    init_schema()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM competitions;")
        total_competitions = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM etl_runs;")
        total_runs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM etl_runs WHERE status = 'success';")
        success_runs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM etl_runs WHERE status = 'failed';")
        failed_runs = cur.fetchone()[0]
        cur.execute(
            """
            SELECT
              id,
              pipeline_name,
              status,
              row_count,
              started_at,
              finished_at,
              error_message,
              CASE
                WHEN finished_at IS NULL THEN NULL
                ELSE ROUND(EXTRACT(EPOCH FROM (finished_at - started_at))::numeric, 3)
              END AS duration_seconds
            FROM etl_runs
            ORDER BY id DESC
            LIMIT 20;
            """
        )
        runs = [
            {
                "id": row[0],
                "pipeline_name": row[1],
                "status": row[2],
                "row_count": row[3],
                "started_at": row[4],
                "finished_at": row[5],
                "error_message": row[6],
                "duration_seconds": row[7],
            }
            for row in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT id, started_at, error_message
            FROM etl_runs
            WHERE status = 'failed'
            ORDER BY id DESC
            LIMIT 5;
            """
        )
        recent_errors = [
            {"id": row[0], "started_at": row[1], "error_message": row[2]}
            for row in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT
              competition_id, season_id, country_name, competition_name, season_name, match_updated
            FROM competitions
            ORDER BY competition_id, season_id
            LIMIT 15;
            """
        )
        competitions_preview = [
            {
                "competition_id": row[0],
                "season_id": row[1],
                "country_name": row[2],
                "competition_name": row[3],
                "season_name": row[4],
                "match_updated": row[5],
            }
            for row in cur.fetchall()
        ]

    latest = runs[0] if runs else None
    return {
        "summary": {
            "total_competitions": total_competitions,
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failed_runs": failed_runs,
        },
        "latest": latest,
        "runs": runs,
        "recent_errors": recent_errors,
        "competitions_preview": competitions_preview,
    }


@app.get("/")
def index():
    data = _fetch_dashboard_data()
    return render_template_string(
        INDEX_TEMPLATE,
        summary=data["summary"],
        latest=data["latest"],
        runs=data["runs"],
        recent_errors=data["recent_errors"],
        competitions_preview=data["competitions_preview"],
        base_url=request.host_url.rstrip("/"),
    )


@app.get("/api/runs")
def runs_api():
    data = _fetch_dashboard_data()
    return jsonify(data)


@app.post("/run/competitions")
def run_competitions():
    result = run_competitions_etl()
    if request.headers.get("Content-Type", "").startswith("application/json"):
        return jsonify(
            {
                "run_id": result.run_id,
                "status": result.status,
                "row_count": result.row_count,
                "error_message": result.error_message,
            }
        )
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
