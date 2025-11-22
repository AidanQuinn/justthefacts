# Repository Guidelines

## Project Structure & Data
- `news_aggregator.py`: end-to-end pipeline (fetch RSS, extract text, cluster via TF-IDF + agglomerative clustering, summarize locally or with OpenAI, publish JSON + RSS).
- `news_data/`: runtime artifacts and cache; `cache.db` (SQLite caches article text and LLM summaries), `stories.json` (latest stories payload), `feed.xml` (generated RSS). Safe to delete for a clean run; the app recreates them.

## Setup, Build, and Run
- Use Python 3.10+ with a virtualenv. Install deps:  
  `python -m venv .venv && source .venv/bin/activate && pip install -U pip feedparser requests numpy scikit-learn feedgen beautifulsoup4 python-dotenv openai trafilatura`
- Optional: disable OpenAI by omitting `OPENAI_API_KEY` or set `use_openai=False` in code; otherwise export `OPENAI_API_KEY` (and optionally `MODEL_NAME=gpt-4o-mini`) in a `.env` file.
- Primary command: `python news_aggregator.py` (fetches feeds, clusters, applies importance filter, writes `news_data/stories.json` and `news_data/feed.xml`).

## Coding Style & Naming
- Follow PEP 8; 4-space indentation; type hints on public functions; prefer dataclasses/config objects for tunables.
- Logging: use the existing `logger` with `.info/.warning/.debug`; avoid bare prints outside the CLI footer. Keep messages concise and action-focused.
- Variables/functions: snake_case; classes: PascalCase; constants: UPPER_SNAKE. Keep helper methods private with a leading underscore when not part of the CLI surface.

## Testing & Verification
- No formal test suite; use a smoke run: `python news_aggregator.py` and confirm `news_data/feed.xml` and `stories.json` refresh without errors. Check logs for fetch/extraction failures and importance filter skips.
- For clustering/summarization tweaks, test with and without `OPENAI_API_KEY` to ensure both local and LLM paths succeed.
- If altering cache/DB schema, verify migrations by deleting `news_data/cache.db` or running twice to ensure idempotent upgrades.

## Commit & PR Guidelines
- Commits: short, imperative subject lines (<=72 chars) focused on one change set; include brief body bullets when behavior changes (e.g., “handle feed fetch timeouts”).
- PRs: include what/why, notable config changes, and before/after behavior. Link issues when available. Add screenshots or sample log excerpts when adjusting output or logging.

## Security & Configuration
- Do not commit real API keys or personally identifiable feed data. Keep `.env` local.
- Network calls hit multiple RSS sources and optional OpenAI; note this in change descriptions if behavior or domains change.***
