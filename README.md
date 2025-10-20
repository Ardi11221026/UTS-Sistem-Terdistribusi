# UTS Pub-Sub Log Aggregator (Deliverable)

**Contents**: FastAPI-based Pub-Sub aggregator with idempotent consumer and SQLite-backed dedup store.

**ZIP name**: uts_pubsub_aggregator.zip

## What is included
- `src/` : application source (FastAPI app, dedup store, models, consumer)
- `tests/` : pytest tests (single file `test_all.py` containing multiple tests)
- `requirements.txt`
- `Dockerfile`
- `README.md` (this file)

## How to run (local, without Docker)
1. Create and activate a Python 3.11+ virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   .\.venv\Scripts\activate # Windows (PowerShell)
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   export DEDUP_DB=./data/dedup.db    # optional, defaults to ./data/dedup.db
   python -m src.main
   ```
   The service will listen on `http://0.0.0.0:8080`.

3. Example publish (single event):
   ```bash
   curl -X POST "http://127.0.0.1:8080/publish" -H "Content-Type: application/json" -d '[{"topic":"t1","event_id":"e1","timestamp":"2025-10-19T12:00:00Z","source":"unit","payload":{"msg":"hello"}}]'
   ```
4. Check processed events:
   ```bash
   curl "http://127.0.0.1:8080/events?topic=t1"
   curl "http://127.0.0.1:8080/stats"
   ```

## How to run tests (pytest)
```bash
pip install -r requirements.txt
pytest -q
```

## How to build Docker image
```bash
docker build -t uts-aggregator .
docker run -p 8080:8080 uts-aggregator
```

## Notes
- Dedup store is SQLite at `DEDUP_DB` (env var) default `./data/dedup.db` and is persistent across restarts.
- Tests create / use a temporary DB under `/tmp` to avoid collisions.
- This project is a minimal, self-contained implementation matching the assignment description.
