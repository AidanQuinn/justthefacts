#!/usr/bin/env python3
"""
Cross-Spectrum News Aggregator (fixed)
- Robust RSS fetching with requests + real UA
- Better logging at each stage
- Do not drop articles when extraction fails; fallback to RSS summary
- Publish even when clusters are singletons
"""

import os
import json
import hashlib
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sqlite3

import feedparser
import requests
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer

# Text extraction
try:
    import trafilatura
except ImportError:
    trafilatura = None

# Optional LLM
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from feedgen.feed import FeedGenerator

# ------ .env (optional) -------
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    print("WARNING: could not load .env file")
    pass

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("news-agg")

# ---------- Config ----------
@dataclass
class Config:
    data_dir: Path = Path("news_data")
    db_path: Path = Path("news_data/cache.db")
    feed_output: Path = Path("news_data/feed.xml")
    json_output: Path = Path("news_data/stories.json")

    # Importance filter
    min_avg_importance: float = 6.0             # require average >= this
    min_any_criterion: float = 0.0              # optional floor per criterion (0 disables)
    importance_weights: Dict[str, float] = None # default set below in __post_init__
    use_llm_importance: bool = True             # set True to ask LLM for ratings (costs tokens)
    llm_importance_top_n: int = 10              # only rate top-N clusters with LLM

    def __post_init__(self):
        # default to equal weights if none provided
        if self.importance_weights is None:
            self.importance_weights = {
                "impact": 1.0,
                "conflict": 1.0,
                "ramifications": 1.0,
                "accountability": 1.0,
                "informed_public": 1.0,
                "citizen_responsibility": 1.0,
                "transparency": 1.0,
            }


    # Clustering
    similarity_threshold: float = 0.6
    min_cluster_size: int = 2
    max_reps_per_lean: int = 5

    # Text limits
    max_text_extract: int = 5000
    max_summary_input: int = 4000

    # Cache settings
    cache_ttl_hours: int = 24

    # API
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    use_openai: bool = bool(os.getenv("OPENAI_API_KEY")) and (OpenAI is not None)
    use_openai_embeddings: bool = True
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_batch_size: int = 32
    embedding_max_items: int = 200

    # LLM control
    llm_top_n: int = 10                 # only strongest N clusters use LLM
    max_llm_retries: int = 2
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ---------- Sources ----------
SOURCES = [
    # Center
    {"name": "AP News", "url": "https://apnews.com/hub/ap-top-news?output=1", "lean": "center"},
    {"name": "BBC", "url": "https://feeds.bbci.co.uk/news/rss.xml", "lean": "center"},

    # Left
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml", "lean": "left"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss", "lean": "left"},
    {"name": "HuffPost", "url": "https://www.huffpost.com/section/front-page/feed", "lean": "left"},

    # Right
    {"name": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/latest.xml", "lean": "right"},
    {"name": "Daily Wire", "url": "https://www.dailywire.com/feeds/rss.xml", "lean": "right"},

    # Tech/business (mixed)
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "lean": "center"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "lean": "center"},
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) NewsAgg/1.0"

# ---------- Aggregator ----------
class NewsAggregator:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.config.data_dir.mkdir(exist_ok=True)
        self.setup_database()

    def setup_database(self):
        """Create/upgrade SQLite schema (idempotent)."""
        conn = sqlite3.connect(self.config.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS article_cache (
                url TEXT PRIMARY KEY,
                title TEXT,
                text TEXT,
                extracted_at_epoch INTEGER,
                source TEXT,
                lean TEXT,
                published TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS story_cache (
                story_id TEXT PRIMARY KEY,
                story_key TEXT,              -- hash of reps
                model_name TEXT,
                summary TEXT,
                created_at_epoch INTEGER
            )
        """)

        # --- MIGRATION: ensure expected columns exist ---
        def ensure_col(table, col, coltype):
            cur = conn.execute(f"PRAGMA table_info({table})")
            cols = {r[1] for r in cur.fetchall()}
            if col not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")

        ensure_col("article_cache", "title", "TEXT")
        ensure_col("article_cache", "text", "TEXT")
        ensure_col("article_cache", "extracted_at_epoch", "INTEGER")
        ensure_col("article_cache", "source", "TEXT")
        ensure_col("article_cache", "lean", "TEXT")
        ensure_col("article_cache", "published", "TEXT")

        ensure_col("story_cache", "story_key", "TEXT")
        ensure_col("story_cache", "model_name", "TEXT")
        ensure_col("story_cache", "summary", "TEXT")
        ensure_col("story_cache", "created_at_epoch", "INTEGER")

        conn.commit()
        conn.close()

    # ---------- Cache helpers ----------
    def _cache_get_article(self, url: str) -> Optional[str]:
        try:
            ttl_sec = self.config.cache_ttl_hours * 3600
            now = int(time.time())
            conn = sqlite3.connect(self.config.db_path)
            cur = conn.execute("SELECT text, extracted_at_epoch FROM article_cache WHERE url = ?", (url,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return None
            text, ts = row
            if ts and (now - int(ts) <= ttl_sec):
                return text
            return None
        except sqlite3.OperationalError:
            # schema changed underneath; treat as cache miss
            return None

    def _cache_put_article(self, article: Dict[str, Any], text: str):
        conn = sqlite3.connect(self.config.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO article_cache (url,title,text,extracted_at_epoch,source,lean,published) VALUES (?,?,?,?,?,?,?)",
            (
                article["url"],
                article["title"],
                text,
                int(time.time()),
                article["source"],
                article["lean"],
                article.get("published", ""),
            ),
        )
        conn.commit()
        conn.close()

    def _story_key_from_reps(self, reps: list) -> str:
        # stable key from reps’ URLs + titles
        payload = [{"u": r["url"], "t": r["title"]} for r in sorted(reps, key=lambda x: x["url"])]
        blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def get_cached_summary(self, story_key: str, model_name: str) -> Optional[str]:
        conn = sqlite3.connect(self.config.db_path)
        cur = conn.execute(
            "SELECT summary FROM story_cache WHERE story_key=? AND model_name=?",
            (story_key, model_name),
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def put_cached_summary(self, story_id: str, story_key: str, model_name: str, summary_text: str):
        conn = sqlite3.connect(self.config.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO story_cache (story_id, story_key, model_name, summary, created_at_epoch) VALUES (?,?,?,?,?)",
            (story_id, story_key, model_name, summary_text, int(time.time())),
        )
        conn.commit()
        conn.close()

    # -------- Fetch --------
    def fetch_feeds(self) -> List[Dict]:
        articles = []
        per_source_counts = []
        for src in SOURCES:
            url = src["url"]
            name = src["name"]
            try:
                resp = requests.get(url, timeout=15, headers={"User-Agent": UA})
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                n = len(feed.entries or [])
                logger.info(f"Fetched {n:>3} entries from {name}")
                per_source_counts.append((name, n))
                for e in feed.entries[:40]:
                    link = e.get("link") or ""
                    title = (e.get("title") or "").strip()
                    if not link or not title:
                        continue
                    summary = (e.get("summary") or e.get("description") or "").strip()
                    articles.append(
                        {
                            "url": link,
                            "title": title,
                            "source": name,
                            "lean": src["lean"],
                            "published": e.get("published", ""),
                            "summary": summary[:600],
                        }
                    )
            except Exception as ex:
                logger.warning(f"{name}: fetch failed ({ex})")
        sources_with_entries = len([c for c in per_source_counts if c[1] > 0])
        logger.info(f"TOTAL raw articles: {len(articles)} (sources with entries: {sources_with_entries}/{len(SOURCES)})")
        return articles

    # -------- Extract --------
    def extract_text(self, article: Dict[str, Any]) -> tuple[str, str]:
        """
        Try full-text extraction (trafilatura -> BeautifulSoup). 
        Only if both fail, fall back to RSS summary. 
        Returns (text, source), where source is 'full' or 'rss'.
        """
        url = article["url"]

        # Cache (full-text only)
        cached = self._cache_get_article(url)
        if cached:
            logger.debug("CACHE HIT (full): %s", url)
            return cached, "full"

        text = ""
        # 1) Try trafilatura
        if trafilatura:
            try:
                downloaded = trafilatura.fetch_url(url, timeout=12)
                if downloaded:
                    text = trafilatura.extract(downloaded, include_comments=False) or ""
            except Exception as ex:
                logger.debug("Trafilatura failed for %s: %s", url, ex)

        # 2) Fallback: BeautifulSoup scrape
        if not text:
            try:
                r = requests.get(url, timeout=12, headers={"User-Agent": UA})
                if r.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, "html.parser")
                    # Drop noisy tags
                    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
                        tag.decompose()
                    node = soup.find("article") or soup.find("main") or soup.body
                    text = node.get_text(separator=" ", strip=True) if node else soup.get_text(" ", strip=True)
            except Exception as ex:
                logger.debug("Fallback scrape failed for %s: %s", url, ex)

        # 3) If full-text found, cache & return
        text = (text or "").strip()
        if text:
            text = text[: self.config.max_text_extract]
            self._cache_put_article(article, text)   # cache only full-text
            return text, "full"

        # 4) Last resort: RSS summary
        rss_text = (article.get("summary") or "").strip()
        rss_text = rss_text[: self.config.max_text_extract]
        return rss_text, "rss"

        # If still empty, fall back to RSS summary
        if not text:
            text = article.get("summary", "")

        text = (text or "")[: self.config.max_text_extract].strip()

        if text:
            self._cache_put_article(article, text)
        return text

    # -------- Embeddings / Clustering --------
    def _embed_texts_openai(self, texts: List[str]) -> Optional[np.ndarray]:
        """Return OpenAI embeddings or None to trigger TF-IDF fallback."""
        if not (self.config.use_openai_embeddings and self.config.use_openai and OpenAI):
            return None
        if len(texts) > self.config.embedding_max_items:
            logger.info("Too many items for OpenAI embeddings (%d > %d); using TF-IDF.",
                        len(texts), self.config.embedding_max_items)
            return None

        logger.info("Using OpenAI embeddings (%s) for %d items", self.config.embedding_model, len(texts))
        client = OpenAI(api_key=self.config.openai_api_key)
        vectors: List[np.ndarray] = []
        delay = 0.6
        for start in range(0, len(texts), self.config.embedding_batch_size):
            batch = texts[start : start + self.config.embedding_batch_size]
            for attempt in range(2):
                try:
                    resp = client.embeddings.create(model=self.config.embedding_model, input=batch)
                    ordered = sorted(resp.data, key=lambda d: d.index)  # preserve order
                    vectors.extend([np.array(item.embedding, dtype=float) for item in ordered])
                    break
                except Exception as ex:
                    if attempt == 0:
                        logger.info("OpenAI embed retry after error: %s", ex)
                        time.sleep(delay)
                        delay *= 2.0
                        continue
                    logger.info("OpenAI embeddings failed; using TF-IDF. (%s)", ex)
                    return None

        if not vectors:
            return None

        mat = np.vstack(vectors)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        return mat / (norms + 1e-10)

    def compute_embeddings(self, texts: List[str]) -> np.ndarray:
        openai_vecs = self._embed_texts_openai(texts)
        if openai_vecs is not None:
            return openai_vecs

        vectorizer = TfidfVectorizer(
            max_features=8000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )
        X = vectorizer.fit_transform(texts).toarray()
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        logger.info("Using TF-IDF embeddings (fallback)")
        return X / (norms + 1e-10)

    def cluster_articles(self, articles: List[Dict], embeddings: np.ndarray) -> List[List[Dict]]:
        if len(articles) < 2:
            return [articles] if articles else []

        # Some sklearn versions use 'affinity' not 'metric'; try metric first, then fallback
        try:
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=1 - self.config.similarity_threshold,
                metric="cosine",
                linkage="complete",  # stricter: merges only when all points are within threshold
            )
        except TypeError:
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=1 - self.config.similarity_threshold,
                affinity="cosine",
                linkage="complete",
            )

        labels = clustering.fit_predict(embeddings)
        clusters: Dict[int, List[Dict]] = {}
        for lbl, art in zip(labels, articles):
            clusters.setdefault(lbl, []).append(art)

        # Keep clusters ≥ min size; if none, fall back to singletons
        valid = [c for c in clusters.values() if len(c) >= self.config.min_cluster_size]
        if not valid:
            logger.info("No multi-article clusters found; publishing singletons.")
            valid = [[a] for a in articles]

        # Second pass: split loose clusters into tighter components
        refined: List[List[Dict]] = []
        for cluster in valid:
            refined.extend(self._subcluster_by_threshold(cluster, embeddings))
        valid = [c for c in refined if len(c) >= self.config.min_cluster_size]
        if not valid:
            valid = refined or [[a] for a in articles]

        valid.sort(key=len, reverse=True)
        logger.info(f"Story clusters: {len(valid)} (from {len(articles)} articles)")
        return valid

    # -------- Representatives --------
    def select_representatives(self, cluster: List[Dict]) -> List[Dict]:
        by_lean: Dict[str, List[Dict]] = {}
        for a in cluster:
            by_lean.setdefault(a["lean"], []).append(a)

        reps: List[Dict] = []
        for lean in ["left", "center", "right"]:
            if lean in by_lean:
                reps.extend(by_lean[lean][: self.config.max_reps_per_lean])
        if not reps:  # fallback
            reps = cluster[: min(len(cluster), 3)]
        return reps

    # -------- Summaries --------
    def summarize_story_local(self, representatives: List[Dict]) -> Dict:
        all_titles = [r["title"] for r in representatives]
        all_texts = [r.get("text") or r.get("summary", "") for r in representatives]
        title = all_titles[0] if all_titles else "News Story"

        lean_counts: Dict[str, int] = {}
        for r in representatives:
            lean_counts[r["lean"]] = lean_counts.get(r["lean"], 0) + 1

        who, what, where, when, why = "Multiple parties", title[:60], "—", datetime.now().strftime("%Y-%m-%d"), "—"
        key_text = " ".join(all_texts)[:1000]

        summary = (
            f"**Who:** {who}\n**What:** {what}\n**Where:** {where}\n**When:** {when}\n**Why:** {why}\n\n"
            f"**Coverage Balance:** Left {lean_counts.get('left',0)} | Center {lean_counts.get('center',0)} | Right {lean_counts.get('right',0)}\n\n"
            f"**Key Points:**\n{key_text[:700]}..."
        )
        summary += self._source_links_block(representatives)

        return {
            "title": title,
            "summary": summary,
            "sources": [{"name": r["source"], "lean": r["lean"], "url": r["url"]} for r in representatives],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _source_links_block(self, representatives: List[Dict]) -> str:
        lines = []
        for r in representatives:
            url = r.get("url", "")
            lines.append(f"- {url}")
        return "\n\nSources:\n" + "\n".join(lines)

    def _with_sources_block(self, summary_text: str, representatives: List[Dict]) -> str:
        block = self._source_links_block(representatives)
        if "Sources:\n-" in summary_text:
            return summary_text
        return summary_text + block

    def summarize_story_openai(self, representatives: List[Dict]) -> Dict:
        # if LLM disabled, fall back
        if not self.config.use_openai or OpenAI is None:
            return self.summarize_story_local(representatives)

        # cache check
        story_key = self._story_key_from_reps(representatives)
        cached = self.get_cached_summary(story_key, self.config.model_name)
        if cached:
            logger.info("Using cached LLM summary for story_key=%s model=%s", story_key[:12], self.config.model_name)
            cached = self._with_sources_block(cached, representatives)
            return {
                "title": representatives[0]["title"],
                "summary": cached,
                "sources": [{"name": r["source"], "lean": r["lean"], "url": r["url"]} for r in representatives],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        client = OpenAI(api_key=self.config.openai_api_key)
        srcs = "\n".join([f"- {r['source']} ({r['lean']}): {r['title']}" for r in representatives])
        texts = "\n\n---\n\n".join(
            [f"[{r['source']}|{r['lean']}] {r['title']}\n{(r.get('text') or r.get('summary',''))[:self.config.max_summary_input]}" for r in representatives]
        )
        prompt = f"""ROLE: Neutral cross-source news summarizer.

SOURCES:
{srcs}

ARTICLES:
{texts}

OUTPUT:
1) Headline (should convey the main thrust of the story)
2) Five bullets (Who/What/Where/When/Why)
3) 3–5 key facts with numbers/dates
4) Where sources agree/disagree (bullets). Only include if >2 distinct sources; cite outlets and lean when noting disagreement. Example: "- **Disagree**: Extent of willingness to negotiate; left/center (Guardian, BBC) say ready to engage, right (Daily Wire) highlights reluctance due to sovereignty concerns."
5) One-paragraph context (most relevant current, historical, economic, political, and/or social)
6) Why this story matters (engaging, concise, factual explanation of how this impacts people in daily life)
Be concise, factual, neutral."""

        # retry with exponential backoff for 429s/quota
        delay = 0.6
        last_err = None
        for attempt in range(self.config.max_llm_retries):
            try:
                resp = client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": "You are a precise, neutral news summarizer."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=700,
                    temperature=0.2,
                )
                txt = resp.choices[0].message.content.strip()
                txt = self._with_sources_block(txt, representatives)
                # save in cache
                story_id = f"llm_{hashlib.sha256((story_key + self.config.model_name).encode()).hexdigest()[:16]}"
                self.put_cached_summary(story_id, story_key, self.config.model_name, txt)
                return {
                    "title": representatives[0]["title"],
                    "summary": txt,
                    "sources": [{"name": r["source"], "lean": r["lean"], "url": r["url"]} for r in representatives],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as ex:
                last_err = ex
                msg = str(ex).lower()
                if "429" in msg or "insufficient_quota" in msg or "rate" in msg:
                    logger.info("LLM 429/quota on attempt %d → backing off %.1fs", attempt + 1, delay)
                    time.sleep(delay)
                    delay *= 2.0
                    continue
                break

        logger.error("OpenAI summarization failed after retries: %s", last_err)
        return self.summarize_story_local(representatives)
    
    # -------- Importance scoring --------
    def _concat_cluster_text(self, cluster: List[Dict], cap_chars: int = 6000) -> str:
        parts = []
        for a in cluster:
            parts.append(a["title"])
            parts.append((a.get("text") or a.get("summary") or "")[:1000])
        text = "\n".join(parts)
        return text[:cap_chars]

    def _source_diversity(self, cluster: List[Dict]) -> float:
        # simple diversity: unique outlets & lean distribution
        outlets = {a["source"] for a in cluster}
        leans = {a["lean"] for a in cluster}
        # scale to 0..1 (more unique = better)
        return min(1.0, (len(outlets) / 4.0 + len(leans) / 3.0) / 2.0)

    def _heuristic_importance(self, cluster: List[Dict]) -> Dict[str, float]:
        """
        Lightweight 1–10 scoring based on keywords, cluster size, source diversity,
        presence of govt/corporate entities, numbers/dates, and verbs that signal stakes.
        """
        import re

        text = (self._concat_cluster_text(cluster)).lower()
        size = len(cluster)
        diversity = self._source_diversity(cluster)

        # quick features
        nums = len(re.findall(r"\b\d{1,4}\b", text))               # numbers/dates
        money = len(re.findall(r"\$\d+|\b(billion|million|trillion)\b", text))
        geo = len(re.findall(r"\b(us|uk|eu|china|india|russia|state|federal|city|county|province)\b", text))
        govt = len(re.findall(r"\b(white house|congress|senate|parliament|ministry|supreme court|regulator|fcc|sec|ftc)\b", text))
        corp = len(re.findall(r"\b(google|apple|amazon|meta|microsoft|exxon|pfizer|boeing|tesla|ford)\b", text))
        conflict_kw = len(re.findall(r"\b(protest|strike|lawsuit|sue|ban|clash|attack|war|sanction|boycott|indict|charges?)\b", text))
        public_info_kw = len(re.findall(r"\b(how to|deadline|register|apply|eligib|recall|evacuate|boil water|polls? open)\b", text))
        wrongdoing_kw = len(re.findall(r"\b(bribe|fraud|corruption|misconduct|cover-?up|whistleblower|leak|investigation|audit)\b", text))
        transparency_kw = len(re.findall(r"\b(leaked|unsealed|newly released|foia|internal memo|whistleblower)\b", text))
        ram_kw = len(re.findall(r"\b(precedent|landmark|sweeping|far-?reaching|nationwide|global)\b", text))

        # normalize helper (0..10)
        def z(val, a, b):
            return max(0.0, min(10.0, 10.0 * (val / b))) if b > 0 else 0.0

        # scores
        impact = min(10.0, 2.0 + z(size, 0, 6) + z(nums + money + geo, 0, 40) + 3.0 * diversity)
        conflict = min(10.0, 1.0 + z(conflict_kw, 0, 10) + z(size, 0, 6))
        ramifications = min(10.0, 1.5 + z(ram_kw + govt + corp, 0, 18))
        accountability = min(10.0, 1.0 + z(wrongdoing_kw + govt, 0, 12))
        informed_public = min(10.0, 1.0 + z(public_info_kw, 0, 8) + 1.5 * diversity)
        citizen_responsibility = min(10.0, z(public_info_kw, 0, 8) + (0.8 if "vote" in text or "election" in text else 0))
        transparency = min(10.0, z(transparency_kw, 0, 6))

        return {
            "impact": round(impact, 1),
            "conflict": round(conflict, 1),
            "ramifications": round(ramifications, 1),
            "accountability": round(accountability, 1),
            "informed_public": round(informed_public, 1),
            "citizen_responsibility": round(citizen_responsibility, 1),
            "transparency": round(transparency, 1),
        }

    def _weighted_average(self, scores: Dict[str, float]) -> float:
        # fall back to equal weights if config is missing
        default_w = {
            "impact": 1.0,
            "conflict": 1.0,
            "ramifications": 1.0,
            "accountability": 1.0,
            "informed_public": 1.0,
            "citizen_responsibility": 1.0,
            "transparency": 1.0,
        }
        w = self.config.importance_weights or default_w
        # only use weights for keys actually present in `scores`
        usable = {k: w.get(k, 0.0) for k in scores.keys()}
        total_w = sum(usable.values()) or 1.0
        s = sum(scores[k] * usable.get(k, 0.0) for k in scores)
        return round(s / total_w, 2)

    def _subcluster_by_threshold(self, cluster: List[Dict], embeddings: np.ndarray) -> List[List[Dict]]:
        """
        Split a cluster into tighter components using a cosine similarity graph.
        Prevents chaining disparate stories together.
        """
        idx_to_article = {a.get("_idx"): a for a in cluster if a.get("_idx") is not None}
        idxs = list(idx_to_article.keys())
        if len(idxs) <= 1:
            return [cluster]

        sub = embeddings[idxs]
        sim = sub @ sub.T  # embeddings are normalized
        n = len(idxs)

        seen = set()
        components: List[List[int]] = []
        for i in range(n):
            if i in seen:
                continue
            stack = [i]
            seen.add(i)
            comp = []
            while stack:
                j = stack.pop()
                comp.append(j)
                for k in range(n):
                    if k in seen:
                        continue
                    if sim[j, k] >= self.config.similarity_threshold:
                        seen.add(k)
                        stack.append(k)
            components.append(comp)

        refined: List[List[Dict]] = []
        for comp in components:
            refined.append([idx_to_article[idxs[pos]] for pos in comp])
        return refined

    def _llm_importance(self, cluster: List[Dict]) -> Optional[Dict[str, float]]:
        if not self.config.use_openai or not self.config.use_llm_importance or OpenAI is None:
            return None
        try:
            client = OpenAI(api_key=self.config.openai_api_key)
            bundle = self._concat_cluster_text(cluster, cap_chars=4500)
            prompt = (
                "Rate this news story on seven 1–10 scales. "
                "Return ONLY JSON with keys: "
                "impact, conflict, ramifications, accountability, informed_public, citizen_responsibility, transparency. "
                "No prose, no comments.\n\n"
                f"STORY:\n{bundle}\n"
            )
            resp = client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "You are an editor scoring news importance. Output JSON only."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.0,
            )
            txt = resp.choices[0].message.content.strip()
            data = json.loads(txt)
            # sanitize to floats 0..10
            keys = ["impact","conflict","ramifications","accountability","informed_public","citizen_responsibility","transparency"]
            out = {k: float(max(0,min(10, data.get(k,0)))) for k in keys}
            return {k: round(v,1) for k,v in out.items()}
        except Exception as ex:
            logger.info("LLM importance rating failed; using heuristics. (%s)", ex)
            return None


    # -------- Publish --------
    def generate_feed(self, stories: List[Dict]) -> str:
        fg = FeedGenerator()
        fg.id("urn:cross-spectrum-news")
        fg.title("Cross-Spectrum News Brief")
        fg.link(href="http://example.com/feed.xml", rel="self")
        fg.description("Balanced news coverage from across the political spectrum")
        fg.language("en")

        now = datetime.now(timezone.utc)
        for story in stories[:20]:
            fe = fg.add_entry()
            fe.id(hashlib.sha256(story["title"].encode()).hexdigest())
            fe.title(story["title"])
            sources_text = "\n\nSources:\n" + "\n".join([f"• {s['name']} ({s['lean']})" for s in story["sources"]])
            fe.description(story["summary"] + sources_text)
            if story["sources"]:
                fe.link(href=story["sources"][0]["url"])
            fe.published(now)

        self.config.feed_output.parent.mkdir(exist_ok=True, parents=True)
        fg.rss_file(str(self.config.feed_output))
        logger.info(f"RSS feed saved to {self.config.feed_output}")
        return str(self.config.feed_output)

    # -------- Run --------
    def run(self):
        logger.info("Starting aggregation...")

        # 1) Fetch
        articles = self.fetch_feeds()
        if not articles:
            logger.warning("No articles fetched from any source. Check network/feeds.")
            return []

        # 2) Extract
        full_count = 0
        rss_count = 0
        kept = 0

        for a in articles:
            text, source = self.extract_text(a)
            if not text:
                # nothing usable — drop later
                a["text"] = ""
                continue

            a["text"] = text
            kept += 1
            if source == "full":
                full_count += 1
                logger.debug("FULL  : %s", a["url"])
            else:
                rss_count += 1
                logger.debug("RSS   : %s", a["url"])

        logger.info("Text source mix: full-text=%d | rss-fallback=%d | total=%d", full_count, rss_count, kept)
        logger.info("Articles with usable text: %d/%d", kept, len(articles))

        # Drop empties after fallback
        articles = [a for a in articles if a["text"]]


        # Drop empties after fallback
        articles = [a for a in articles if a["text"]]

        # 3) Dedup by URL
        uniq = []
        seen = set()
        for a in articles:
            if a["url"] not in seen:
                seen.add(a["url"])
                uniq.append(a)
        articles = uniq
        logger.info(f"Unique articles after dedup: {len(articles)}")

        if not articles:
            logger.warning("After extraction/dedup, no articles remain.")
            return []

        # 4) Embeddings
        for i, a in enumerate(articles):
            a["_idx"] = i  # preserve position for downstream clustering checks
        texts = [f"{a['title']} {a['text'][:600]}" for a in articles]
        embeddings = self.compute_embeddings(texts)

        # 5) Cluster
        clusters = self.cluster_articles(articles, embeddings)

        # 6) Score importance, filter, then summarize
        stories = []
        kept = 0
        skipped = 0

        for i, cluster in enumerate(clusters[:25]):
            reps = self.select_representatives(cluster)
            if not reps:
                continue

            # importance: try LLM for top-N (if enabled), else heuristics
            scores = None
            if self.config.use_llm_importance and i < self.config.llm_importance_top_n:
                logger.info("LLM importance scoring for cluster %d", i + 1)
                scores = self._llm_importance(cluster)
            if not scores:
                if self.config.use_llm_importance and i < self.config.llm_importance_top_n:
                    logger.info("Falling back to heuristic importance for cluster %d", i + 1)
                scores = self._heuristic_importance(cluster)

            avg_score = self._weighted_average(scores)

            # per-criterion floor
            passes_floor = all(v >= self.config.min_any_criterion for v in scores.values())
            if (avg_score < self.config.min_avg_importance) or (not passes_floor):
                skipped += 1
                logger.info("Skip cluster %d: avg=%.2f scores=%s", i+1, avg_score, scores)
                continue

            use_llm_now = (not getattr(self, "llm_disabled_for_run", False)) and self.config.use_openai and (i < self.config.llm_top_n)
            logger.info("Summarizing cluster %d with %s (size=%d)", i + 1, "LLM" if use_llm_now else "local", len(cluster))
            story = self.summarize_story_openai(reps) if use_llm_now else self.summarize_story_local(reps)
            story["cluster_size"] = len(cluster)
            story["story_id"] = f"story_{i}_{datetime.now().strftime('%Y%m%d')}"
            story["importance_scores"] = scores
            story["importance_avg"] = avg_score
            stories.append(story)
            kept += 1

            logger.info("Story %d: %s... (cluster %d, LLM=%s, avg=%.2f, scores=%s)",
                        i + 1, story["title"][:70], len(cluster), "yes" if use_llm_now else "no", avg_score, scores)

        logger.info("Importance filter: kept=%d, skipped=%d", kept, skipped)


        # 7) Save JSON
        self.config.json_output.parent.mkdir(exist_ok=True, parents=True)
        with open(self.config.json_output, "w") as f:
            json.dump(stories, f, indent=2)
        logger.info(f"Stories JSON saved: {self.config.json_output}")

        # 8) Feed
        if stories:
            self.generate_feed(stories)
        else:
            logger.warning("No stories produced; feed not generated.")

        logger.info(f"Done. Articles: {len(articles)} | Clusters: {len(clusters)} | Stories: {len(stories)}")
        return stories

# ---------- CLI ----------
def main():
    cfg = Config()
    logger.info("Using trafilatura: %s", "Yes" if trafilatura else "No")
    logger.info("Using LLM: %s", "Yes" if cfg.use_openai else "No")
    if cfg.use_openai:
        logger.info("Model: %s", cfg.model_name)
    agg = NewsAggregator(cfg)
    stories = agg.run()

    if stories:
        print("\n" + "=" * 60)
        print("TOP STORY")
        print("=" * 60)
        print("Title:", stories[0]["title"])
        print("Sources:", len(stories[0]["sources"]))
        print("\nSummary:\n", stories[0]["summary"][:600], "...")
        print("\nSee:", cfg.feed_output)
    else:
        print("No stories produced. Check logs above.")

if __name__ == "__main__":
    main()
