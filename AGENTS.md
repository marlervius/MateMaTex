# AGENTS.md

## Cursor Cloud specific instructions

### Product overview
MateMaTeX is an AI-powered math education content generator for Norwegian schools (LK20 curriculum). It has two architectures:
- **v1 (Streamlit):** Monolithic app at `app.py` + `src/`, uses CrewAI with Google Gemini. Port 8501.
- **v2 (Next.js + FastAPI):** `frontend/` (Next.js 14, port 3000) + `backend/` (FastAPI, port 8000). Uses LangGraph, Supabase for auth/DB.

### Running services

| Service | Command | Port |
|---------|---------|------|
| FastAPI backend | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` | 8000 |
| Next.js frontend | `cd frontend && npx next dev --port 3000` | 3000 |
| Streamlit v1 | `streamlit run app.py --server.port 8501 --server.headless true` | 8501 |

### Key caveats
- The backend starts without a database (`DATABASE_URL` empty is OK); it logs a warning and disables DB features.
- The frontend redirects unauthenticated users to `/login` (HTTP 307) — this is expected, not an error.
- `~/.local/bin` must be on `PATH` for `ruff`, `black`, `streamlit`, `uvicorn`, `pytest` commands. The update script handles this.
- Frontend has no lockfile; `npm install` is used. An `.eslintrc.json` (`{"extends": "next/core-web-vitals"}`) must exist in `frontend/` to avoid interactive ESLint prompts during `next lint`.
- Python 3.12 is required (see `runtime.txt`).
- 3 pre-existing test failures in `backend/tests/` (math verifier fraction edge case, pipeline routing assertion) are known issues, not env problems.

### Lint / Test / Build commands
- **Python lint:** `ruff check .` and `black --check .` (from repo root)
- **Frontend lint:** `cd frontend && npx next lint`
- **Backend tests:** `cd backend && python3 -m pytest tests/ -v`
- **Frontend build:** `cd frontend && npx next build`
- **CI mirrors:** See `.github/workflows/ci.yml` for the canonical lint + compile check pipeline.
