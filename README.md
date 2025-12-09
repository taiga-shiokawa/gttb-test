# GitHub To Tech Blog (GTTB)

Generate tech blog drafts from GitHub pull requests with a FastAPI backend and lightweight Jinja UI.

## What is included
- FastAPI app with endpoints to generate drafts from a GitHub PR URL and to view saved history.
- SQLModel models for storing generated drafts (SQLite by default, PostgreSQL ready).
- Service stubs for GitHub REST API and LLM integrations (OpenAI), with graceful fallbacks when keys are missing.
- Simple Jinja-based UI for submitting a PR URL and viewing generation results.

## Quickstart
1. Python 3.11+.
2. Create and activate a virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment template and set secrets:
   ```bash
   cp .env.example .env
   # fill GITHUB_TOKEN, OPENAI_API_KEY, DATABASE_URL as needed
   ```
5. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Open http://localhost:8000 to use the UI or http://localhost:8000/docs for the Swagger UI.

## Configuration
- `DATABASE_URL`: PostgreSQL URL for production (e.g. `postgresql+psycopg://user:pass@host:5432/db`). Defaults to local SQLite for development.
- `GITHUB_TOKEN`: Personal Access Token with `repo` read scope for GitHub API requests.
- `OPENAI_API_KEY`: Used for LLM text generation. When unset, the app returns a placeholder draft.

## Development notes
- Data model lives in `app/models.py`; DB setup in `app/db.py`.
- GitHub and LLM clients are in `app/services/`.
- API routes are grouped under `app/routers/` (`generate` for PR ingestion, `history` for saved drafts).
- Templates and static assets live in `app/templates` and `app/static`.
- Logging and error handling are kept minimal for MVP; extend as needed for production.
