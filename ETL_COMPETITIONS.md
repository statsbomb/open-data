# ETL competitions (phase 1)

Ce module charge `data/competitions.json` vers PostgreSQL et expose une interface web locale pour le suivi.

## 1) Prérequis

- Python 3.10+
- PostgreSQL accessible localement ou à distance

## 2) Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Configuration

Définir la variable d'environnement `DATABASE_URL`:

```bash
export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/statsbomb'
```

## 4) Lancer l'ETL competitions

```bash
python run_competitions_etl.py
```

## 5) Lancer l'interface de suivi (URL)

```bash
python app.py
```

Puis ouvrir:

`http://127.0.0.1:8000`

Actions disponibles:
- lancer un run competitions
- voir le statut des derniers runs
- suivre le nombre de lignes chargées dans la table `competitions`

## Schéma chargé (phase 1)

- `competitions`: données métier + `raw_payload`
- `etl_runs`: journal des exécutions
