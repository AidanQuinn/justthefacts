# Just the Facts — Cross-Spectrum News Aggregator

Balanced news summaries from multiple political leans. The pipeline fetches RSS feeds, extracts article text, clusters related coverage, scores importance, and publishes concise, neutral summaries.

## Quick Start
- Prereqs: Python 3.10+, virtualenv recommended.
- Install deps:
  ```
  python -m venv .venv && source .venv/bin/activate
  pip install -U pip feedparser requests numpy scikit-learn feedgen beautifulsoup4 python-dotenv openai trafilatura
  ```
- Env: create `.env` with `OPENAI_API_KEY=...` and optionally `MODEL_NAME=gpt-4o-mini` and `EMBEDDING_MODEL=text-embedding-3-small`. Without a key, the app falls back to local summaries and TF-IDF embeddings.
- Run: `python news_aggregator.py`

## What It Does
- Fetches up to 40 items from each source (AP, Reuters, BBC, NPR, Guardian, HuffPost, Fox News, Daily Wire, TechCrunch, Ars Technica) with a real User-Agent.
- Extracts full text (trafilatura → BeautifulSoup fallback) or uses RSS summary; caches in `news_data/cache.db` for 24h.
- Embeds (OpenAI by default; TF-IDF fallback), clusters with cosine distance, filters by importance, and summarizes.
- Outputs:
  - `news_data/stories.json`: structured stories with sources and scores.
  - `news_data/feed.xml`: RSS feed for distribution.

## Key Config (in `news_aggregator.py`)
- Embeddings: `use_openai_embeddings=True`, `embedding_model="text-embedding-3-small"`, `embedding_max_items=200`.
- Clustering: `similarity_threshold=0.6`, `min_cluster_size=2`, complete linkage with a second-pass tightener.
- Summaries: LLM up to top 10 clusters (`llm_top_n`), local fallback otherwise; per-article summary input capped at 4000 chars.
- Importance: heuristic scores with optional LLM ranking; requires average ≥ 6.0 to publish.

## Tips
- If feeds change, update `SOURCES` URLs in `news_aggregator.py`.
- Delete `news_data/cache.db` to reset caches or after schema changes.
- Watch logs for fetch failures or rate limits; OpenAI calls have a retry/backoff and will fall back gracefully.***
