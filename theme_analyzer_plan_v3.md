# Financial News Theme Analysis Tool - FINAL REVISED PLAN

**Last Updated**: December 28, 2025
**Status**: Ready for Implementation
**Platform**: Windows (with CPU-only PyTorch)

---

## Quick Start (Windows)

```powershell
# 1. Clone/create the project directory
cd C:\Users\Admin\OneDrive\DesktopLuke\Programming\finance

# 2. Run the setup script (installs CPU-only PyTorch + all dependencies)
.\scripts\setup.ps1

# 3. Add your Gemini API key
copy .env.example .env
notepad .env  # Add your key from https://aistudio.google.com/apikey

# 4. Activate environment and run
.\venv\Scripts\Activate.ps1

# Collector mode: Run hourly via Task Scheduler (no LLM calls)
python main.py --collector

# Analyzer mode: Run once at EOD (LLM analysis)
python main.py --run-eod
```

---

## Executive Summary

**Goal**: Build a terminal-based investment tool that aggregates financial news from RSS feeds, uses Gemini 3 Flash to identify emerging investment themes, and provides Bloomberg Terminal-style output with reliable citations and multi-source confirmation.

**Key Architecture Decisions**:
1. **Decoupled ingestion and analysis**: Continuous RSS polling stores articles without LLM calls; single EOD run performs deep analysis.
2. **Greedy collection, bounded analysis**: Collect as many articles as RSS exposes (100-300+/day); analyze only 50-80 selected articles.
3. **Vector clustering BEFORE API calls**: Reduces costs by 85-90%.
4. **Deterministic quality gates**: Prevent "trash sampling" with info-density scoring and source diversity enforcement.

**Tech Stack**:
| Component | Technology | Why |
|-----------|------------|-----|
| AI Engine | Gemini 3 Flash (`gemini-3-flash-preview`) | Best price/performance, 1M context |
| Clustering | sentence-transformers + AgglomerativeClustering | Local, fast, accurate |
| RSS Parsing | feedparser + trafilatura | Robust with fallback |
| Persistence | SQLite | Article storage + theme decay tracking |
| Terminal UI | rich library | Bloomberg-style output |
| Language | Python 3.10+ | Your primary language |

---

## Ingestion Schedule & Coverage

### Design Rationale

RSS feeds have **limited item retention**. A typical financial news feed shows only the 20-50 most recent items. At EOD, a single fetch might only capture articles from the last 2-4 hours, missing morning and midday coverage entirely.

**Problem: Feed Eviction**
- Morning story published at 09:00 KST
- 50 more stories published throughout the day
- Evening fetch at 23:30 KST: morning story is gone

**Solution: Continuous Collection**
- Poll RSS feeds every 30-60 minutes
- Store all unique articles to SQLite immediately
- EOD analysis queries the full 24-28 hour window from storage, not from live RSS

### Two-Mode Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              COLLECTOR MODE                                     │
│                    (Scheduled: every 30-60 min, no LLM)                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  RSS Feeds ─────► Fetch ─────► Dedupe ─────► Store to SQLite                  │
│                     │                              │                          │
│                     │                              ▼                          │
│                     │                     articles table                       │
│                     │                     (guid, url, content, fetched_at)    │
│                     │                                                         │
│                     └──► Detect truncation risk ──► Log warning               │
│                                                                               │
│  Cost: $0.00 (no LLM calls)                                                   │
│  Time: ~30 seconds per run                                                    │
│                                                                               │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                              ANALYZER MODE                                      │
│                    (Scheduled: once at EOD, e.g., 23:30 KST)                   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  SQLite ─► Query last 28h ─► Deterministic Selection ─► Card-based Selection  │
│                                   (free)                   (1 LLM call)        │
│                                      │                          │              │
│                                      ▼                          ▼              │
│                               Candidate pool              Selected set         │
│                               (~150-300)                   (~80 articles)      │
│                                                                 │              │
│                                                                 ▼              │
│  Selected ──► Cluster ──► Theme Extraction ──► Validate ──► Score ──► Report │
│                              (5-7 LLM calls)                                   │
│                                                                                │
│  Cost: ~$0.10-0.15 (6-8 LLM calls total)                                      │
│  Time: ~60-90 seconds                                                          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Feed Truncation Risk Detection

When a feed returns near its maximum item count AND the oldest item timestamp is newer than the lookback start, the system flags a **TRUNCATION_RISK** warning.

```python
def detect_truncation_risk(
    feed_entries: List[dict],
    source_name: str,
    lookback_start: datetime,
    max_items_threshold: int = 40
) -> Optional[TruncationWarning]:
    """
    Detect if a feed may have lost articles due to eviction.

    Returns a warning if:
    1. Feed returned >= max_items_threshold entries
    2. Oldest entry is newer than lookback_start

    This indicates articles may have been pushed out before we fetched them.
    """
    if len(feed_entries) < max_items_threshold:
        return None

    oldest_entry = min(feed_entries, key=lambda e: e.get('published_parsed', datetime.max))
    oldest_time = datetime(*oldest_entry['published_parsed'][:6])

    if oldest_time > lookback_start:
        gap_hours = (oldest_time - lookback_start).total_seconds() / 3600
        return TruncationWarning(
            source=source_name,
            entries_returned=len(feed_entries),
            oldest_entry_time=oldest_time,
            lookback_start=lookback_start,
            gap_hours=gap_hours,
            recommendation=f"Increase poll frequency for {source_name} or add supplementary sources"
        )

    return None
```

### Collector Mode Schedule (Windows Task Scheduler)

```powershell
# Create scheduled task to run collector every hour
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "main.py --collector" `
    -WorkingDirectory "C:\Users\Admin\OneDrive\DesktopLuke\Programming\finance"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 60) `
    -RepetitionDuration (New-TimeSpan -Days 365)

Register-ScheduledTask -TaskName "FinanceNewsCollector" `
    -Action $action -Trigger $trigger -Description "Hourly RSS collection"
```

---

## Cost Analysis (December 2025)

### Gemini 3 Flash API Pricing

| Mode | Input | Output | Notes |
|------|-------|--------|-------|
| **On-demand** | $0.50 / 1M tokens | $3.00 / 1M tokens | Standard pay-as-you-go |
| **Batch API** | Lower rates | Lower rates | Async processing, check current pricing |
| **Context caching** | Reduced input cost | N/A | Separate cached input + storage fees |

> **Note**: Caching and batch modes have distinct pricing structures that vary by model and region.
> Check [Google's current pricing page](https://ai.google.dev/gemini-api/docs/pricing) for exact rates.

### Free Tier Warning

Google's free tier is **not reliable for production use**. Rate limits are restrictive and subject to change without notice. Budget for paid API access for any production workload.

### Per-Run Cost Estimate (EOD Analysis)

```
80 selected articles → 6-8 clusters → 7-9 API calls

Card Selection Call:
  Input:  ~15,000 tokens × $0.50/1M  = $0.008

Theme Extraction (6-8 clusters):
  Input:  ~70,000 tokens × $0.50/1M  = $0.035
  Output: ~15,000 tokens × $3.00/1M  = $0.045
────────────────────────────────────────────
Estimated per EOD run:               ~$0.09-0.12
```

### Monthly Projections

| Usage Pattern | Collector Runs | EOD Runs | Estimated Monthly Cost |
|---------------|----------------|----------|------------------------|
| Daily analysis | 720 (hourly) | 30 | ~$2.70-3.60 |
| Twice daily EOD | 720 (hourly) | 60 | ~$5.40-7.20 |

> Collector mode has zero LLM cost. All spend is in Analyzer mode.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            RSS FEEDS (Data Sources)                              │
│  Bloomberg Markets • CNBC • Yahoo Finance • Investing.com • MarketWatch         │
└──────────────────────────────────┬───────────────────────────────────────────────┘
                                   │
                        ┌──────────┴──────────┐
                        ▼                     ▼
┌───────────────────────────────┐   ┌─────────────────────────────────────────────┐
│      COLLECTOR MODE           │   │              ANALYZER MODE                   │
│  (Hourly, no LLM, $0)         │   │        (EOD, LLM calls, ~$0.10)             │
├───────────────────────────────┤   ├─────────────────────────────────────────────┤
│                               │   │                                             │
│  ┌─────────────────────────┐  │   │  ┌─────────────────────────────────────┐   │
│  │   rss_fetcher.py        │  │   │  │  Query SQLite (last 28h)            │   │
│  │   • Fetch all feeds     │  │   │  │  → ~150-400 collected articles       │   │
│  │   • Rate limiting       │  │   │  └─────────────────────────────────────┘   │
│  │   • Truncation check    │  │   │                     │                      │
│  └───────────┬─────────────┘  │   │                     ▼                      │
│              │                │   │  ┌─────────────────────────────────────┐   │
│              ▼                │   │  │  SELECTION STAGE (NEW)              │   │
│  ┌─────────────────────────┐  │   │  │                                     │   │
│  │   article_extractor.py  │  │   │  │  Step A: Deterministic Pruning     │   │
│  │   • trafilatura         │  │   │  │    • Remove low-info articles       │   │
│  │   • RSS fallback        │  │   │  │    • Info-density scoring          │   │
│  │   • Mark content_mode   │  │   │  │    • Output: ~150-200 candidates    │   │
│  └───────────┬─────────────┘  │   │  │                                     │   │
│              │                │   │  │  Step B: Card-Based LLM Selection  │   │
│              ▼                │   │  │    • 1 Gemini call                  │   │
│  ┌─────────────────────────┐  │   │  │    • Select K=80 articles           │   │
│  │   Dedupe & Store        │  │   │  │    • Enforce diversity rules        │   │
│  │   • URL/GUID dedupe     │  │   │  │                                     │   │
│  │   • Assign dup_group_id │  │   │  └─────────────────────────────────────┘   │
│  │   • Write to SQLite     │  │   │                     │                      │
│  └─────────────────────────┘  │   │                     ▼                      │
│                               │   │  ┌─────────────────────────────────────┐   │
│  Output: articles table       │   │  │  CLUSTERING (selected only)         │   │
│          runs table           │   │  │  • Vectorize → Cluster              │   │
└───────────────────────────────┘   │  │  • Min 3 articles + 2 publishers    │   │
                                    │  │  • Output: 5-8 clusters             │   │
                                    │  └─────────────────────────────────────┘   │
                                    │                     │                      │
                                    │                     ▼                      │
                                    │  ┌─────────────────────────────────────┐   │
                                    │  │  THEME EXTRACTION                   │   │
                                    │  │  • 1 Gemini call per cluster        │   │
                                    │  │  • VERBATIM quote requirement       │   │
                                    │  │  • Citation validation               │   │
                                    │  └─────────────────────────────────────┘   │
                                    │                     │                      │
                                    │                     ▼                      │
                                    │  ┌─────────────────────────────────────┐   │
                                    │  │  SYNTHESIS                          │   │
                                    │  │  • Aggregate & dedupe themes        │   │
                                    │  │  • Calculate confidence scores      │   │
                                    │  │  • Enforce source diversity         │   │
                                    │  └─────────────────────────────────────┘   │
                                    │                     │                      │
                                    │                     ▼                      │
                                    │  ┌─────────────────────────────────────┐   │
                                    │  │  PRESENTATION                       │   │
                                    │  │  • Bloomberg-style terminal         │   │
                                    │  │  • Trend indicators (NEW/FADING)    │   │
                                    │  │  • Low-signal-day warnings          │   │
                                    │  └─────────────────────────────────────┘   │
                                    └─────────────────────────────────────────────┘
```

---

## Directory Structure

```
finance/
├── scripts/
│   ├── setup.ps1                # Windows PowerShell setup (recommended)
│   ├── setup.bat                # Windows Command Prompt setup (alternative)
│   └── schedule_collector.ps1   # Create Windows Task Scheduler job (NEW)
├── config/
│   ├── __init__.py
│   ├── settings.py              # Central config, env vars, thresholds
│   └── rss_sources.json         # RSS feed definitions (verified Dec 2025)
├── src/
│   ├── __init__.py
│   ├── models.py                # Article, Cluster, Theme, Citation dataclasses
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py       # Fetch RSS with rate limiting + truncation check
│   │   └── article_extractor.py # Extract content with fallback
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── article_parser.py    # Clean and validate text
│   │   ├── deduplicator.py      # Remove syndicated duplicates
│   │   └── clustering.py        # Vector clustering (CRITICAL)
│   ├── selection/               # NEW STAGE
│   │   ├── __init__.py
│   │   ├── info_density.py      # Deterministic quality scoring
│   │   ├── candidate_pruner.py  # Filter low-quality articles
│   │   └── card_selector.py     # LLM-based final selection
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── gemini_client.py     # Gemini 3 Flash API wrapper
│   │   └── theme_extractor.py   # Prompt engineering + citation validation
│   ├── synthesis/
│   │   ├── __init__.py
│   │   ├── theme_aggregator.py  # Deduplicate themes across clusters
│   │   └── confidence_scorer.py # Calculate 0-100 reliability scores
│   ├── storage/
│   │   ├── __init__.py
│   │   └── db.py                # SQLite persistence for articles + themes
│   └── presentation/
│       ├── __init__.py
│       ├── terminal_formatter.py # Bloomberg-style output
│       └── report_generator.py   # Text/JSON export
├── data/
│   └── finance.db               # SQLite database (articles + themes + runs)
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Structured logging
│   └── rate_limiter.py          # Domain-aware rate limiting
├── main.py                      # CLI entry point (--collector / --run-eod)
├── requirements.txt             # See Windows note about PyTorch
├── .env.example                 # Template for API keys
├── .env                         # Actual API keys (git-ignored)
├── .gitignore
└── README.md
```

---

## Component Specifications

### 1. Configuration (`config/settings.py`)

```python
"""Central configuration management."""
import os
from pathlib import Path
from datetime import time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Timezone
KST = ZoneInfo("Asia/Seoul")

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-3-flash-preview"  # December 2025 release

# ============================================================================
# COLLECTOR MODE SETTINGS
# ============================================================================
POLL_INTERVAL_MINUTES = 60           # How often to run collector (cron/scheduler)
LOOKBACK_HOURS_COLLECTOR = 2         # How far back to look in each poll
FEED_MAX_ITEMS_THRESHOLD = 40        # Truncation warning if feed returns >= this

# ============================================================================
# ANALYZER MODE SETTINGS (EOD)
# ============================================================================
EOD_RUN_TIME_KST = time(23, 30)      # Default EOD run time (Asia/Seoul)
LOOKBACK_HOURS_EOD = 28              # Query window for EOD analysis (28h for safety)

# Selection Stage
CANDIDATE_POOL_SIZE = 200            # Max candidates after deterministic pruning
TARGET_SELECTED_ARTICLES = 80        # Articles sent to clustering/LLM analysis
MAX_ARTICLES_PER_SOURCE = 10         # Diversity cap per publisher in selection
MAX_TIME_CONCENTRATION = 0.40        # Max 40% of selected from last 6 hours

# Low Signal Day Detection
LOW_SIGNAL_CLUSTERS_THRESHOLD = 5    # Fewer clusters = low signal warning
LOW_SIGNAL_SUMMARY_ONLY_RATIO = 0.6  # >60% paywall/summary-only = warning

# ============================================================================
# INGESTION SETTINGS
# ============================================================================
RSS_RATE_LIMIT_RPM = 10              # Requests per minute per domain
PAYWALL_FALLBACK_MIN_CHARS = 200     # Trigger RSS description fallback

# ============================================================================
# PROCESSING SETTINGS
# ============================================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # 80MB, fast, good enough
CLUSTERING_DISTANCE_THRESHOLD = 0.6  # Tune: lower = more clusters
CLUSTERING_MIN_ARTICLES = 3          # Minimum articles per cluster
CLUSTERING_MIN_UNIQUE_PUBLISHERS = 2 # NEW: Require 2+ publishers per cluster
ARTICLE_MIN_WORDS = 100              # Minimum words for valid article

# ============================================================================
# ANALYSIS SETTINGS
# ============================================================================
CITATION_FUZZY_MATCH_THRESHOLD = 0.85
GEMINI_TEMPERATURE = 0.3             # Lower for factual analysis
GEMINI_MAX_OUTPUT_TOKENS = 8192

# ============================================================================
# SYNTHESIS SETTINGS
# ============================================================================
THEME_SIMILARITY_THRESHOLD = 0.80    # For deduplication

# ============================================================================
# STORAGE SETTINGS
# ============================================================================
DB_PATH = DATA_DIR / "finance.db"    # Unified database
THEME_DECAY_DAYS = 7                 # Mark as "fading" if not updated

# ============================================================================
# SOURCE QUALITY TIERS
# ============================================================================
# NOTE: These are publisher quality rankings, NOT RSS feed availability.
# - Tier 1: Highest credibility financial news sources
# - Tier 2: Reputable but may have more opinion/aggregation content
#
# Reuters is Tier 1 quality but has no public RSS (discontinued ~2020).
TIER_1_SOURCES = ["Bloomberg", "CNBC", "Financial Times", "Reuters", "Wall Street Journal"]
TIER_2_SOURCES = ["Yahoo Finance", "MarketWatch", "Investing.com", "Seeking Alpha"]

# RSS Feeds Actually Available (subset of above)
RSS_AVAILABLE_TIER_1 = ["Bloomberg", "CNBC"]  # FT has limited RSS
RSS_AVAILABLE_TIER_2 = ["Yahoo Finance", "MarketWatch", "Investing.com", "Seeking Alpha"]

# ============================================================================
# INFO-DENSITY SCORING WEIGHTS (Selection Stage)
# ============================================================================
DENSITY_WEIGHTS = {
    "numbers_ratio": 2.0,            # Higher = more numeric data
    "entity_hits": 1.5,              # Ticker symbols, company names
    "causal_verbs": 1.0,             # "caused", "led to", "resulted"
    "opinion_penalty": -3.0,         # "I think", "in my opinion"
    "listicle_penalty": -2.0,        # "5 stocks to buy", "top 10"
    "newsletter_penalty": -2.0,      # Promotional content
    "short_article_penalty": -1.5,   # < 300 words
}
```

### 2. RSS Sources (`config/rss_sources.json`)

```json
{
  "sources": [
    {
      "name": "Bloomberg Markets",
      "url": "https://feeds.bloomberg.com/markets/news.rss",
      "category": "general_markets",
      "tier": 1,
      "priority": 1
    },
    {
      "name": "CNBC Top News",
      "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
      "category": "general_markets",
      "tier": 1,
      "priority": 1
    },
    {
      "name": "Yahoo Finance",
      "url": "https://finance.yahoo.com/news/rssindex",
      "category": "general_markets",
      "tier": 2,
      "priority": 1
    },
    {
      "name": "Investing.com Analysis",
      "url": "https://www.investing.com/rss/news_285.rss",
      "category": "analysis",
      "tier": 2,
      "priority": 2
    },
    {
      "name": "MarketWatch Top Stories",
      "url": "http://feeds.marketwatch.com/marketwatch/topstories/",
      "category": "general_markets",
      "tier": 2,
      "priority": 2
    },
    {
      "name": "Seeking Alpha Market News",
      "url": "https://seekingalpha.com/market_currents.xml",
      "category": "market_currents",
      "tier": 2,
      "priority": 2
    }
  ],
  "fetch_limits": {
    "max_articles_per_source": 50,
    "lookback_hours": 28
  },
  "_notes": {
    "reuters": "Reuters does not provide public RSS (discontinued ~2020). Only include with licensed feeds.",
    "verified": "All feeds tested December 2025"
  }
}
```

### 3. Data Models (`src/models.py`)

```python
"""Type-safe data structures for the analysis pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class ContentMode(Enum):
    """How article content was obtained."""
    FULL = "full"              # Full article extracted via trafilatura
    SUMMARY_ONLY = "summary"   # Paywall fallback - RSS description only

@dataclass
class Article:
    """Represents a single news article."""
    guid: str                       # RSS guid or URL hash (unique identifier)
    url: str
    canonical_url: Optional[str]    # Resolved URL after redirects
    title: str
    summary: str                    # RSS description
    source: str                     # e.g., "Bloomberg Markets"
    published_date: datetime
    fetched_at: datetime            # When we collected this article

    full_text: Optional[str] = None
    content_mode: ContentMode = ContentMode.SUMMARY_ONLY
    content_hash: Optional[str] = None  # MD5 of full_text for change detection

    # Syndication detection
    dup_group_id: Optional[int] = None  # Articles in same group are syndicated copies

    # Source metadata
    tier: int = 2                   # Source quality tier (1 or 2)

    # Selection stage scoring
    info_density_score: float = 0.0
    word_count: int = 0

    # HTTP caching
    etag: Optional[str] = None
    last_modified: Optional[str] = None

@dataclass
class ArticleCard:
    """
    Lightweight representation for LLM selection stage.

    Contains just enough info for Gemini to make selection decisions
    without sending full article text (saves tokens).
    """
    id: int                         # Database row ID
    source: str
    tier: int
    published_time: str             # ISO format
    title: str
    summary_snippet: str            # First 150 chars of summary
    key_sentences: List[str]        # 1-2 most informative sentences
    density_score: float
    dup_group_id: Optional[int]
    content_mode: str               # "full" or "summary"

@dataclass
class Cluster:
    """Represents a group of semantically similar articles."""
    cluster_id: int
    articles: List[Article]
    centroid_text: str              # Representative text for the cluster
    unique_publishers: int          # Count of unique sources
    estimated_tokens: int = 0

@dataclass
class Citation:
    """A verified quote from a source article."""
    article_title: str
    quote: str                      # VERBATIM quote from article
    url: str
    source: str
    published_date: datetime
    is_verified: bool = True        # Passed fuzzy match validation

@dataclass
class Theme:
    """An investment theme extracted from news analysis."""
    theme_name: str
    industries: List[str]           # GICS sectors
    reasoning: str                  # 2-3 sentence investment thesis
    citations: List[Citation]
    confidence: str                 # HIGH / MEDIUM / LOW
    sentiment: str                  # BULLISH / BEARISH / NEUTRAL
    confidence_score: float = 0.0   # 0-100 numeric score

    # Persistence fields (populated from DB)
    first_detected: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    mention_count: int = 1
    trend_status: str = "NEW"       # NEW / STABLE / FADING

@dataclass
class TruncationWarning:
    """Warning that a feed may have lost articles due to eviction."""
    source: str
    entries_returned: int
    oldest_entry_time: datetime
    lookback_start: datetime
    gap_hours: float
    recommendation: str

@dataclass
class CollectorRunStats:
    """Statistics for a single collector run."""
    run_id: int
    run_timestamp: datetime
    sources_fetched: int
    entries_found: int
    new_articles_stored: int
    duplicates_skipped: int
    truncation_warnings: List[TruncationWarning]
    duration_seconds: float

@dataclass
class AnalyzerRunStats:
    """Statistics for a single EOD analyzer run."""
    run_id: int
    run_date: str                   # YYYY-MM-DD (Asia/Seoul)
    run_timestamp: datetime
    lookback_hours: int

    # Collection stats
    collected_count: int            # Total articles in lookback window
    unique_count: int               # After URL/content deduplication

    # Selection stats
    candidate_count: int            # After deterministic pruning
    selected_count: int             # After card-based selection
    summary_only_ratio: float       # % of selected that are paywall/summary-only

    # Analysis stats
    cluster_count: int
    themes_extracted: int
    llm_calls: int
    token_usage_input: int
    token_usage_output: int
    estimated_cost_usd: float

    # Quality signals
    is_low_signal_day: bool
    low_signal_reasons: List[str]

    processing_time_seconds: float

@dataclass
class AnalysisResult:
    """Complete output of an EOD analysis run."""
    stats: AnalyzerRunStats
    themes: List[Theme]
    truncation_warnings: List[TruncationWarning]
```

### 4. SQLite Schema (`src/storage/db.py`)

```python
"""SQLite persistence for articles, themes, and run statistics."""
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from contextlib import contextmanager
from src.models import Article, Theme, ContentMode, CollectorRunStats, AnalyzerRunStats
from config.settings import DB_PATH, THEME_DECAY_DAYS

# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

SCHEMA = """
-- Articles table: stores all collected articles across runs
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Unique identifiers
    guid TEXT NOT NULL,                    -- RSS guid or computed hash
    url TEXT NOT NULL,
    canonical_url TEXT,                    -- Resolved URL after redirects

    -- Content
    title TEXT NOT NULL,
    summary TEXT NOT NULL,                 -- RSS description
    full_text TEXT,                        -- Extracted full article (may be NULL)
    content_mode TEXT NOT NULL DEFAULT 'summary',  -- 'full' or 'summary'
    content_hash TEXT,                     -- MD5 of full_text for change detection

    -- Source metadata
    source TEXT NOT NULL,                  -- Publisher name
    tier INTEGER NOT NULL DEFAULT 2,       -- Source quality tier

    -- Timestamps
    published_at TIMESTAMP NOT NULL,       -- Article publication time
    fetched_at TIMESTAMP NOT NULL,         -- When we collected it

    -- HTTP caching
    etag TEXT,
    last_modified TEXT,

    -- Syndication detection
    dup_group_id INTEGER,                  -- Articles in same group are syndicated

    -- Selection stage
    info_density_score REAL DEFAULT 0.0,
    word_count INTEGER DEFAULT 0,

    -- Constraints
    UNIQUE(guid, source)                   -- Same article can appear in multiple sources
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_fetched ON articles(fetched_at);
CREATE INDEX IF NOT EXISTS idx_articles_dup_group ON articles(dup_group_id);
CREATE INDEX IF NOT EXISTS idx_articles_guid ON articles(guid);

-- Themes table: stores extracted themes with lifecycle tracking
CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    sentiment TEXT NOT NULL,
    industries TEXT NOT NULL,              -- Comma-separated GICS sectors
    reasoning TEXT,
    first_detected TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    mention_count INTEGER DEFAULT 1,
    last_confidence_score REAL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_themes_last_updated ON themes(last_updated);
CREATE INDEX IF NOT EXISTS idx_themes_name ON themes(name);

-- Collector runs: tracks each hourly collection run
CREATE TABLE IF NOT EXISTS collector_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TIMESTAMP NOT NULL,
    sources_fetched INTEGER NOT NULL,
    entries_found INTEGER NOT NULL,
    new_articles_stored INTEGER NOT NULL,
    duplicates_skipped INTEGER NOT NULL,
    truncation_warnings TEXT,              -- JSON array of warnings
    duration_seconds REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_collector_runs_timestamp ON collector_runs(run_timestamp);

-- Analyzer runs: tracks each EOD analysis run
CREATE TABLE IF NOT EXISTS analyzer_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT NOT NULL,                -- YYYY-MM-DD (Asia/Seoul)
    run_timestamp TIMESTAMP NOT NULL,
    lookback_hours INTEGER NOT NULL,

    -- Collection stats
    collected_count INTEGER NOT NULL,
    unique_count INTEGER NOT NULL,

    -- Selection stats
    candidate_count INTEGER NOT NULL,
    selected_count INTEGER NOT NULL,
    summary_only_ratio REAL NOT NULL,

    -- Analysis stats
    cluster_count INTEGER NOT NULL,
    themes_extracted INTEGER NOT NULL,
    llm_calls INTEGER NOT NULL,
    token_usage_input INTEGER NOT NULL,
    token_usage_output INTEGER NOT NULL,
    estimated_cost_usd REAL NOT NULL,

    -- Quality signals
    is_low_signal_day BOOLEAN NOT NULL DEFAULT 0,
    low_signal_reasons TEXT,               -- JSON array

    processing_time_seconds REAL NOT NULL,

    UNIQUE(run_date)                       -- One EOD run per day
);

CREATE INDEX IF NOT EXISTS idx_analyzer_runs_date ON analyzer_runs(run_date);

-- Article-to-run mapping (for analyzer runs)
CREATE TABLE IF NOT EXISTS run_articles (
    run_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    was_selected BOOLEAN NOT NULL DEFAULT 0,  -- True if article was in final selection
    cluster_id INTEGER,                       -- Which cluster it was assigned to

    PRIMARY KEY (run_id, article_id),
    FOREIGN KEY (run_id) REFERENCES analyzer_runs(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);
"""

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """Initialize the database schema."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)

# ============================================================================
# ARTICLE OPERATIONS
# ============================================================================

def compute_guid(url: str, title: str) -> str:
    """Compute a stable GUID for an article without RSS guid."""
    content = f"{url}|{title}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def article_exists(guid: str, source: str) -> bool:
    """Check if an article already exists in the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM articles WHERE guid = ? AND source = ?",
            (guid, source)
        )
        return cursor.fetchone() is not None

def insert_article(article: Article) -> int:
    """Insert a new article and return its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO articles (
                guid, url, canonical_url, title, summary, full_text,
                content_mode, content_hash, source, tier, published_at,
                fetched_at, etag, last_modified, dup_group_id,
                info_density_score, word_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.guid,
            article.url,
            article.canonical_url,
            article.title,
            article.summary,
            article.full_text,
            article.content_mode.value,
            article.content_hash,
            article.source,
            article.tier,
            article.published_date,
            article.fetched_at,
            article.etag,
            article.last_modified,
            article.dup_group_id,
            article.info_density_score,
            article.word_count
        ))
        return cursor.lastrowid

def get_articles_in_window(
    lookback_hours: int,
    end_time: Optional[datetime] = None
) -> List[Article]:
    """
    Get all articles within the lookback window.

    Queries by published_at, not fetched_at, to ensure consistent
    coverage regardless of when collection happened.
    """
    if end_time is None:
        end_time = datetime.utcnow()

    start_time = end_time - timedelta(hours=lookback_hours)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles
            WHERE published_at >= ? AND published_at <= ?
            ORDER BY published_at DESC
        """, (start_time, end_time))

        rows = cursor.fetchall()
        return [_row_to_article(row) for row in rows]

def _row_to_article(row: sqlite3.Row) -> Article:
    """Convert a database row to an Article object."""
    return Article(
        guid=row["guid"],
        url=row["url"],
        canonical_url=row["canonical_url"],
        title=row["title"],
        summary=row["summary"],
        source=row["source"],
        published_date=datetime.fromisoformat(row["published_at"]),
        fetched_at=datetime.fromisoformat(row["fetched_at"]),
        full_text=row["full_text"],
        content_mode=ContentMode(row["content_mode"]),
        content_hash=row["content_hash"],
        dup_group_id=row["dup_group_id"],
        tier=row["tier"],
        info_density_score=row["info_density_score"],
        word_count=row["word_count"],
        etag=row["etag"],
        last_modified=row["last_modified"]
    )

# ============================================================================
# THEME OPERATIONS
# ============================================================================

def upsert_theme(theme: Theme) -> None:
    """Insert or update a theme in the database."""
    now = datetime.utcnow()
    industries_str = ",".join(theme.industries)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, mention_count FROM themes WHERE name = ?",
            (theme.theme_name,)
        )
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE themes SET
                    last_updated = ?,
                    mention_count = ?,
                    sentiment = ?,
                    industries = ?,
                    reasoning = ?,
                    last_confidence_score = ?
                WHERE id = ?
            """, (
                now,
                row["mention_count"] + 1,
                theme.sentiment,
                industries_str,
                theme.reasoning,
                theme.confidence_score,
                row["id"]
            ))
        else:
            cursor.execute("""
                INSERT INTO themes
                (name, sentiment, industries, reasoning, first_detected,
                 last_updated, mention_count, last_confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                theme.theme_name,
                theme.sentiment,
                industries_str,
                theme.reasoning,
                now,
                now,
                theme.confidence_score
            ))

def determine_trend_status(theme_name: str) -> str:
    """Determine if a theme is NEW, STABLE, or FADING."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT first_detected, last_updated FROM themes WHERE name = ?",
            (theme_name,)
        )
        row = cursor.fetchone()

        if not row:
            return "NEW"

        first_detected = datetime.fromisoformat(row["first_detected"])
        last_updated = datetime.fromisoformat(row["last_updated"])
        now = datetime.utcnow()

        if (now - first_detected).days == 0:
            return "NEW"

        if (now - last_updated).days >= THEME_DECAY_DAYS:
            return "FADING"

        return "STABLE"

# ============================================================================
# RUN STATISTICS
# ============================================================================

def save_collector_run(stats: CollectorRunStats) -> int:
    """Save collector run statistics."""
    import json

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO collector_runs (
                run_timestamp, sources_fetched, entries_found,
                new_articles_stored, duplicates_skipped,
                truncation_warnings, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.run_timestamp,
            stats.sources_fetched,
            stats.entries_found,
            stats.new_articles_stored,
            stats.duplicates_skipped,
            json.dumps([w.__dict__ for w in stats.truncation_warnings]) if stats.truncation_warnings else None,
            stats.duration_seconds
        ))
        return cursor.lastrowid

def save_analyzer_run(stats: AnalyzerRunStats) -> int:
    """Save analyzer run statistics."""
    import json

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analyzer_runs (
                run_date, run_timestamp, lookback_hours,
                collected_count, unique_count, candidate_count, selected_count,
                summary_only_ratio, cluster_count, themes_extracted,
                llm_calls, token_usage_input, token_usage_output,
                estimated_cost_usd, is_low_signal_day, low_signal_reasons,
                processing_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.run_date,
            stats.run_timestamp,
            stats.lookback_hours,
            stats.collected_count,
            stats.unique_count,
            stats.candidate_count,
            stats.selected_count,
            stats.summary_only_ratio,
            stats.cluster_count,
            stats.themes_extracted,
            stats.llm_calls,
            stats.token_usage_input,
            stats.token_usage_output,
            stats.estimated_cost_usd,
            stats.is_low_signal_day,
            json.dumps(stats.low_signal_reasons) if stats.low_signal_reasons else None,
            stats.processing_time_seconds
        ))
        return cursor.lastrowid
```

### 5. Selection Stage - Info Density Scoring (`src/selection/info_density.py`)

```python
"""
Deterministic info-density scoring for article quality assessment.

This module provides a FAST, FREE quality score for each article before
any LLM calls are made. Articles with low info-density are pruned from
the candidate pool, reducing wasted LLM spend on low-value content.

Rationale:
- Market wraps with no specific data points = low value
- Opinion/newsletter content = subjective, not factual
- Listicles ("5 stocks to buy") = SEO content, not analysis
- Short stubs = insufficient evidence for themes
- Number-dense articles = specific data points, high value
"""
import re
from typing import List, Tuple
from src.models import Article, ContentMode
from config.settings import DENSITY_WEIGHTS

# Regex patterns for scoring
PATTERNS = {
    "numbers": re.compile(r'\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?%|\b\d{1,3}(?:,\d{3})+\b'),
    "tickers": re.compile(r'\b[A-Z]{1,5}(?:\.[A-Z])?\b(?=\s|,|\.|\)|$)'),
    "causal": re.compile(r'\b(caused|led to|resulted in|due to|because of|driven by|sparked|triggered)\b', re.I),
    "opinion": re.compile(r'\b(I think|in my opinion|I believe|seems to me|arguably)\b', re.I),
    "listicle": re.compile(r'\b(\d+\s+(?:stocks?|ways?|reasons?|tips?)\s+to|top\s+\d+|best\s+\d+)\b', re.I),
    "newsletter": re.compile(r'\b(subscribe|newsletter|sign up|premium|members only)\b', re.I),
}

def calculate_info_density(article: Article) -> Tuple[float, dict]:
    """
    Calculate information density score for an article.

    Returns:
        Tuple of (score: float, breakdown: dict)

    Score components:
    - numbers_ratio: % of text that is numeric data
    - entity_hits: count of ticker symbols / company names
    - causal_verbs: count of causal language patterns
    - opinion_penalty: negative if opinion language detected
    - listicle_penalty: negative if listicle patterns detected
    - newsletter_penalty: negative if promotional content detected
    - short_article_penalty: negative if < 300 words
    """
    text = article.full_text or article.summary
    word_count = len(text.split())
    article.word_count = word_count

    breakdown = {}

    # Numbers density (higher = more specific data)
    numbers = PATTERNS["numbers"].findall(text)
    numbers_ratio = len(numbers) / max(word_count, 1) * 100
    breakdown["numbers_ratio"] = numbers_ratio

    # Entity/ticker hits
    tickers = PATTERNS["tickers"].findall(text)
    entity_hits = len(set(tickers))  # Unique tickers
    breakdown["entity_hits"] = entity_hits

    # Causal language (indicates analysis, not just reporting)
    causal_matches = PATTERNS["causal"].findall(text)
    causal_verbs = len(causal_matches)
    breakdown["causal_verbs"] = causal_verbs

    # Penalties
    breakdown["opinion_penalty"] = -1 if PATTERNS["opinion"].search(text) else 0
    breakdown["listicle_penalty"] = -1 if PATTERNS["listicle"].search(text) else 0
    breakdown["newsletter_penalty"] = -1 if PATTERNS["newsletter"].search(text) else 0
    breakdown["short_article_penalty"] = -1 if word_count < 300 else 0

    # Summary-only penalty (paywall fallback has less evidence)
    breakdown["summary_only_penalty"] = -1 if article.content_mode == ContentMode.SUMMARY_ONLY else 0

    # Calculate weighted score
    score = 0.0
    for key, value in breakdown.items():
        weight = DENSITY_WEIGHTS.get(key.replace("_penalty", "_penalty"), 1.0)
        if "_penalty" in key:
            weight = DENSITY_WEIGHTS.get(key, -1.0)
        score += value * weight

    # Normalize to 0-100 range
    score = max(0, min(100, score * 5 + 50))

    return score, breakdown

def score_articles(articles: List[Article]) -> List[Article]:
    """
    Calculate info-density scores for all articles.

    Modifies articles in-place and returns sorted by score descending.
    """
    for article in articles:
        score, _ = calculate_info_density(article)
        article.info_density_score = score

    return sorted(articles, key=lambda a: a.info_density_score, reverse=True)
```

### 6. Selection Stage - Candidate Pruner (`src/selection/candidate_pruner.py`)

```python
"""
Deterministic candidate pruning before LLM selection.

This module reduces the article pool from ~150-400 collected articles
to ~150-200 candidates using ZERO LLM calls. The remaining candidates
are then sent to the card-based LLM selection stage.

Pruning rules (in order):
1. Remove articles with info_density_score < 30 (absolute floor)
2. Remove duplicate content (same content_hash)
3. Apply per-source cap to prevent single-source dominance
4. Keep top CANDIDATE_POOL_SIZE by score
"""
from typing import List, Set
from collections import defaultdict
from src.models import Article
from config.settings import CANDIDATE_POOL_SIZE, MAX_ARTICLES_PER_SOURCE

MIN_DENSITY_SCORE = 30  # Absolute floor for quality

def prune_candidates(articles: List[Article]) -> List[Article]:
    """
    Prune articles to candidate pool size using deterministic rules.

    This function does NOT call any LLM. All filtering is rule-based.

    Returns:
        List of candidate articles (max CANDIDATE_POOL_SIZE)
    """
    # Step 1: Remove low-density articles
    candidates = [a for a in articles if a.info_density_score >= MIN_DENSITY_SCORE]

    # Step 2: Remove content duplicates (same hash)
    seen_hashes: Set[str] = set()
    unique_candidates = []
    for article in candidates:
        if article.content_hash:
            if article.content_hash in seen_hashes:
                continue
            seen_hashes.add(article.content_hash)
        unique_candidates.append(article)
    candidates = unique_candidates

    # Step 3: Apply per-source cap (but keep highest-scoring per source)
    # Sort by (source, -score) so we keep best from each source
    source_counts: defaultdict[str, int] = defaultdict(int)
    source_capped = []

    # First pass: sort by score descending globally
    candidates.sort(key=lambda a: a.info_density_score, reverse=True)

    for article in candidates:
        if source_counts[article.source] < MAX_ARTICLES_PER_SOURCE * 2:
            # Allow 2x cap at this stage; LLM selection will enforce final cap
            source_capped.append(article)
            source_counts[article.source] += 1

    candidates = source_capped

    # Step 4: Keep top N by score
    candidates = candidates[:CANDIDATE_POOL_SIZE]

    return candidates

def get_pruning_stats(original: List[Article], pruned: List[Article]) -> dict:
    """Return statistics about what was pruned."""
    return {
        "original_count": len(original),
        "pruned_count": len(pruned),
        "removed_count": len(original) - len(pruned),
        "low_density_removed": sum(1 for a in original if a.info_density_score < MIN_DENSITY_SCORE),
        "sources_in_pool": len(set(a.source for a in pruned)),
    }
```

### 7. Selection Stage - Card-Based LLM Selection (`src/selection/card_selector.py`)

```python
"""
LLM-based article selection using compact "article cards".

This module makes ONE Gemini call to select the final K articles from
the candidate pool. Instead of sending full article text, we send
compact "cards" with just enough info for selection decisions.

Rationale:
- Full articles = 50,000+ tokens → expensive
- Article cards = ~5,000 tokens → 10x cheaper
- LLM can assess relevance from title + summary + key metrics
- Diversity constraints are enforced in the prompt

Selection constraints (enforced by LLM + validated in code):
1. max_per_source: No more than N articles from same publisher
2. time_distribution: No more than 40% from last 6 hours
3. dup_group_avoidance: Don't select multiple from same dup_group_id
4. content_mode_preference: Prefer "full" over "summary_only" when tied
"""
import json
from typing import List, Set
from datetime import datetime, timedelta
from src.models import Article, ArticleCard
from src.analysis.gemini_client import send_selection_request, count_tokens
from config.settings import (
    TARGET_SELECTED_ARTICLES,
    MAX_ARTICLES_PER_SOURCE,
    MAX_TIME_CONCENTRATION
)

def build_article_card(article: Article, db_id: int) -> ArticleCard:
    """Convert an Article to a compact ArticleCard for LLM selection."""
    # Extract 1-2 key sentences (first and most number-dense)
    text = article.full_text or article.summary
    sentences = text.split('. ')
    key_sentences = []

    if sentences:
        key_sentences.append(sentences[0][:200])  # First sentence

        # Find most number-dense sentence
        import re
        number_pattern = re.compile(r'\$[\d,]+|\d+(?:\.\d+)?%')
        scored = [(s, len(number_pattern.findall(s))) for s in sentences]
        scored.sort(key=lambda x: x[1], reverse=True)
        if scored and scored[0][1] > 0 and scored[0][0] != sentences[0]:
            key_sentences.append(scored[0][0][:200])

    return ArticleCard(
        id=db_id,
        source=article.source,
        tier=article.tier,
        published_time=article.published_date.isoformat(),
        title=article.title,
        summary_snippet=article.summary[:150],
        key_sentences=key_sentences,
        density_score=article.info_density_score,
        dup_group_id=article.dup_group_id,
        content_mode=article.content_mode.value
    )

def build_selection_prompt(cards: List[ArticleCard], target_k: int) -> str:
    """Build the prompt for LLM article selection."""
    now = datetime.utcnow()
    six_hours_ago = now - timedelta(hours=6)

    cards_json = json.dumps([
        {
            "id": c.id,
            "source": c.source,
            "tier": c.tier,
            "time": c.published_time,
            "title": c.title,
            "snippet": c.summary_snippet,
            "keys": c.key_sentences,
            "score": round(c.density_score, 1),
            "dup_group": c.dup_group_id,
            "mode": c.content_mode
        }
        for c in cards
    ], indent=2)

    return f"""You are selecting financial news articles for investment theme analysis.

From the {len(cards)} candidate articles below, select exactly {target_k} articles that:
1. Cover the most significant market-moving stories
2. Provide substantive analysis with specific data points
3. Represent diverse sources and time coverage

HARD CONSTRAINTS (you MUST follow these):
- max_per_source = {MAX_ARTICLES_PER_SOURCE} (no more than {MAX_ARTICLES_PER_SOURCE} articles from any single source)
- time_spread: max {int(MAX_TIME_CONCENTRATION * 100)}% of selections can be from the last 6 hours (before {six_hours_ago.isoformat()})
- dup_group: if multiple articles share the same dup_group (non-null), select only ONE from that group
- prefer mode="full" over mode="summary" when relevance is similar

SOFT PREFERENCES:
- Higher tier sources (tier=1) are more authoritative
- Higher density_score indicates more substantive content
- Prefer articles with specific numbers, percentages, or company names

ARTICLES:
{cards_json}

Return ONLY a JSON object with this exact structure:
{{
  "selected_ids": [list of {target_k} article IDs as integers],
  "source_counts": {{"source_name": count, ...}},
  "recent_6h_count": <number of selected articles from last 6 hours>
}}

Respond with valid JSON only. No explanation or markdown."""

def select_articles(
    candidates: List[Article],
    article_ids: List[int]
) -> List[int]:
    """
    Select final articles using LLM-based card selection.

    Args:
        candidates: List of candidate Article objects
        article_ids: Corresponding database IDs for each article

    Returns:
        List of selected database IDs
    """
    # Build cards
    cards = [
        build_article_card(article, db_id)
        for article, db_id in zip(candidates, article_ids)
    ]

    # Build prompt
    prompt = build_selection_prompt(cards, TARGET_SELECTED_ARTICLES)

    # Call Gemini
    response = send_selection_request(prompt)

    # Parse response
    selected_ids = response.get("selected_ids", [])

    # Validate constraints (LLM might not follow perfectly)
    selected_ids = _validate_selection(
        selected_ids, cards, article_ids
    )

    return selected_ids

def _validate_selection(
    selected_ids: List[int],
    cards: List[ArticleCard],
    all_ids: List[int]
) -> List[int]:
    """
    Validate and fix LLM selection to meet hard constraints.

    If LLM violated constraints, we fix them deterministically.
    """
    id_to_card = {c.id: c for c in cards}

    # Filter to valid IDs only
    valid_ids = [id for id in selected_ids if id in id_to_card]

    # Enforce per-source cap
    source_counts: dict[str, int] = {}
    source_capped = []
    for id in valid_ids:
        card = id_to_card[id]
        count = source_counts.get(card.source, 0)
        if count < MAX_ARTICLES_PER_SOURCE:
            source_capped.append(id)
            source_counts[card.source] = count + 1
    valid_ids = source_capped

    # Enforce dup_group uniqueness
    seen_groups: Set[int] = set()
    group_deduped = []
    for id in valid_ids:
        card = id_to_card[id]
        if card.dup_group_id is not None:
            if card.dup_group_id in seen_groups:
                continue
            seen_groups.add(card.dup_group_id)
        group_deduped.append(id)
    valid_ids = group_deduped

    # Enforce time concentration
    now = datetime.utcnow()
    six_hours_ago = now - timedelta(hours=6)
    max_recent = int(len(valid_ids) * MAX_TIME_CONCENTRATION)

    recent_ids = []
    older_ids = []
    for id in valid_ids:
        card = id_to_card[id]
        pub_time = datetime.fromisoformat(card.published_time)
        if pub_time >= six_hours_ago:
            recent_ids.append(id)
        else:
            older_ids.append(id)

    # If too many recent, trim to limit
    if len(recent_ids) > max_recent:
        # Keep highest-scoring recent articles
        recent_ids.sort(key=lambda id: id_to_card[id].density_score, reverse=True)
        recent_ids = recent_ids[:max_recent]

    valid_ids = older_ids + recent_ids

    # If we're under target, add more from candidates
    if len(valid_ids) < TARGET_SELECTED_ARTICLES:
        remaining = [id for id in all_ids if id not in valid_ids]
        remaining_cards = [id_to_card.get(id) for id in remaining if id in id_to_card]
        remaining_cards = [c for c in remaining_cards if c is not None]
        remaining_cards.sort(key=lambda c: c.density_score, reverse=True)

        for card in remaining_cards:
            if len(valid_ids) >= TARGET_SELECTED_ARTICLES:
                break
            if source_counts.get(card.source, 0) < MAX_ARTICLES_PER_SOURCE:
                if card.dup_group_id is None or card.dup_group_id not in seen_groups:
                    valid_ids.append(card.id)
                    source_counts[card.source] = source_counts.get(card.source, 0) + 1
                    if card.dup_group_id:
                        seen_groups.add(card.dup_group_id)

    return valid_ids[:TARGET_SELECTED_ARTICLES]
```

**Rationale for Card-Based Selection**:

This stage exists to solve a fundamental tension: we want to analyze enough articles for reliable theme detection (~80), but we also want maximum coverage of the day's news (could be 300+ unique articles).

Without this stage, we'd either:
- Send 300+ full articles to Gemini → expensive, noisy
- Randomly sample 80 → might miss important stories
- Use only deterministic scoring → can't assess "relevance" to market-moving events

The card-based approach gives us:
- LLM judgment on relevance at low cost (~5K tokens vs ~50K for full articles)
- Enforced diversity constraints validated in code
- Full transparency: we can audit which articles were selected and why

### 8. Gemini Client (`src/analysis/gemini_client.py`)

```python
"""Gemini 3 Flash API wrapper using the google-genai SDK with Structured Outputs."""
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from typing import List, Optional
import json
import logging

from config.settings import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_OUTPUT_TOKENS
)

logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic models for Structured Outputs
# ============================================================================

class CitationSchema(BaseModel):
    """Schema for a single citation."""
    article_title: str
    quote: str
    url: str

class ThemeSchema(BaseModel):
    """Schema for an extracted theme."""
    theme_name: str
    industries: List[str]
    reasoning: str
    citations: List[CitationSchema]
    confidence: str
    sentiment: str

class AnalysisResponseSchema(BaseModel):
    """Top-level response schema for theme extraction."""
    theme: ThemeSchema

class SelectionResponseSchema(BaseModel):
    """Response schema for article selection."""
    selected_ids: List[int]
    source_counts: dict
    recent_6h_count: int

# ============================================================================
# Client setup
# ============================================================================

_client: Optional[genai.Client] = None

def get_client() -> genai.Client:
    """Lazy-load the Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass

class GeminiValidationError(Exception):
    """Custom exception for response validation failures."""
    pass

# ============================================================================
# Token counting
# ============================================================================

def count_tokens(text: str) -> int:
    """
    Count tokens using Gemini's token counting API.

    Falls back to chars/4 estimation if API call fails.
    """
    try:
        client = get_client()
        response = client.models.count_tokens(
            model=GEMINI_MODEL,
            contents=text
        )
        return response.total_tokens
    except Exception as e:
        logger.warning(f"Token counting API failed, using estimation: {e}")
        return len(text) // 4

# ============================================================================
# API requests
# ============================================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((GeminiAPIError,)),
    reraise=True
)
def send_analysis_request(prompt: str) -> dict:
    """
    Send a theme extraction prompt to Gemini.

    Uses Structured Outputs with JSON Schema for reliable parsing.
    """
    client = get_client()

    config = types.GenerateContentConfig(
        temperature=GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        response_schema=AnalysisResponseSchema,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )

        text = response.text or ""

        if not text.strip():
            raise GeminiAPIError("Empty response from Gemini")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")
            data = _attempt_json_repair(text)

        try:
            validated = AnalysisResponseSchema.model_validate(data)
            return validated.model_dump()
        except ValidationError as e:
            logger.warning(f"Pydantic validation failed: {e}")
            if "theme" in data:
                return data
            raise GeminiValidationError(f"Response validation failed: {e}")

    except Exception as e:
        error_str = str(e).lower()
        if "429" in str(e) or "quota" in error_str:
            raise GeminiAPIError(f"Rate limited: {e}") from e
        if "503" in str(e) or "overloaded" in error_str:
            raise GeminiAPIError(f"Service overloaded: {e}") from e
        raise GeminiAPIError(f"Gemini API error: {e}") from e

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((GeminiAPIError,)),
    reraise=True
)
def send_selection_request(prompt: str) -> dict:
    """
    Send an article selection prompt to Gemini.

    Lower temperature for more deterministic selection.
    """
    client = get_client()

    config = types.GenerateContentConfig(
        temperature=0.1,  # Very low for consistent selection
        max_output_tokens=2048,
        response_mime_type="application/json",
        response_schema=SelectionResponseSchema,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )

        text = response.text or ""

        if not text.strip():
            raise GeminiAPIError("Empty response from Gemini")

        return json.loads(text)

    except Exception as e:
        error_str = str(e).lower()
        if "429" in str(e) or "quota" in error_str:
            raise GeminiAPIError(f"Rate limited: {e}") from e
        raise GeminiAPIError(f"Gemini API error: {e}") from e

def _attempt_json_repair(text: str) -> dict:
    """Attempt to repair malformed JSON response."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise GeminiAPIError(f"Could not repair JSON: {text[:200]}...")

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate API cost in USD (on-demand pricing)."""
    input_cost = (input_tokens / 1_000_000) * 0.50
    output_cost = (output_tokens / 1_000_000) * 3.00
    return input_cost + output_cost
```

### 9. Clustering with Publisher Diversity (`src/processing/clustering.py`)

```python
"""Vector-based article clustering to reduce API calls."""
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from src.models import Article, Cluster
from config.settings import (
    EMBEDDING_MODEL,
    CLUSTERING_DISTANCE_THRESHOLD,
    CLUSTERING_MIN_ARTICLES,
    CLUSTERING_MIN_UNIQUE_PUBLISHERS
)

_model: SentenceTransformer = None

def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def vectorize_articles(articles: List[Article]) -> np.ndarray:
    """Convert articles to vector embeddings."""
    model = get_embedding_model()

    texts = [
        f"{article.title}. {article.summary[:500]}"
        for article in articles
    ]

    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings

def cluster_articles(articles: List[Article]) -> List[Cluster]:
    """
    Group semantically similar articles into clusters.

    Filters clusters by:
    - Minimum article count (CLUSTERING_MIN_ARTICLES)
    - Minimum unique publishers (CLUSTERING_MIN_UNIQUE_PUBLISHERS)

    This ensures themes have multi-source confirmation.
    """
    if len(articles) < CLUSTERING_MIN_ARTICLES:
        return []

    embeddings = vectorize_articles(articles)

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=CLUSTERING_DISTANCE_THRESHOLD,
        metric='euclidean',
        linkage='average'
    )

    labels = clustering.fit_predict(normalized)

    cluster_map: dict[int, List[Article]] = {}
    for idx, label in enumerate(labels):
        if label not in cluster_map:
            cluster_map[label] = []
        cluster_map[label].append(articles[idx])

    clusters: List[Cluster] = []
    for cluster_id, cluster_articles in cluster_map.items():
        # Count unique publishers
        unique_publishers = len(set(a.source for a in cluster_articles))

        # Apply both filters
        if (len(cluster_articles) >= CLUSTERING_MIN_ARTICLES and
            unique_publishers >= CLUSTERING_MIN_UNIQUE_PUBLISHERS):

            best_article = min(cluster_articles, key=lambda a: a.tier)

            cluster = Cluster(
                cluster_id=cluster_id,
                articles=cluster_articles,
                centroid_text=best_article.title,
                unique_publishers=unique_publishers,
                estimated_tokens=estimate_cluster_tokens(cluster_articles)
            )
            clusters.append(cluster)

    return clusters

def estimate_cluster_tokens(articles: List[Article]) -> int:
    """Estimate token count for a cluster."""
    from src.analysis.gemini_client import count_tokens

    combined_text = "\n\n".join(
        f"{a.title}\n{a.summary}\n{a.full_text or ''}"
        for a in articles
    )
    return count_tokens(combined_text)
```

### 10. Theme Extractor (`src/analysis/theme_extractor.py`)

```python
"""Prompt engineering for accurate theme extraction with citations."""
import json
from typing import List, Tuple
from difflib import SequenceMatcher
from src.models import Cluster, Theme, Citation
from src.analysis.gemini_client import send_analysis_request
from config.settings import CITATION_FUZZY_MATCH_THRESHOLD

SYSTEM_PROMPT = """You are a quantitative financial analyst at a top investment bank.
Your task is to extract actionable investment themes from clustered news articles.

CRITICAL REQUIREMENTS:
1. Extract ONE primary investment theme from this cluster
2. Include EXACT VERBATIM quotes from the articles as citations
3. Use GICS sector names for industries
4. Return ONLY valid JSON - no markdown, no preamble, no explanation
5. Be specific and actionable - not generic observations

Your citations will be validated against source text. Fabricated quotes will be rejected."""

USER_PROMPT_TEMPLATE = """Analyze this cluster of {count} semantically related articles from {publisher_count} unique publishers about: "{centroid}"

ARTICLES:
{articles_formatted}

Extract the primary investment theme. Return this exact JSON structure:
{{
  "theme": {{
    "theme_name": "Specific actionable theme name (5-10 words)",
    "industries": ["GICS Sector 1", "GICS Sector 2"],
    "reasoning": "2-3 sentences explaining the investment thesis and why this matters for portfolio positioning",
    "citations": [
      {{
        "article_title": "Exact article title",
        "quote": "EXACT VERBATIM quote from the article (15-50 words)",
        "url": "Article URL"
      }}
    ],
    "confidence": "HIGH|MEDIUM|LOW",
    "sentiment": "BULLISH|BEARISH|NEUTRAL"
  }}
}}

Confidence guide:
- HIGH: 3+ sources confirm the theme with specific data points
- MEDIUM: 2 sources with consistent messaging
- LOW: Single source or conflicting information

Sentiment guide:
- BULLISH: Positive catalyst for asset prices
- BEARISH: Negative catalyst for asset prices
- NEUTRAL: Informational without clear directional impact"""

def format_articles_for_prompt(articles: List) -> str:
    """Format articles for inclusion in prompt."""
    formatted = []
    for i, article in enumerate(articles, 1):
        text = article.full_text or article.summary
        text = text[:2000] if len(text) > 2000 else text

        formatted.append(f"""
--- Article {i} ---
Title: {article.title}
Source: {article.source}
Date: {article.published_date.strftime('%Y-%m-%d %H:%M UTC')}
URL: {article.url}
Content: {text}
""")
    return "\n".join(formatted)

def fuzzy_quote_match(quote: str, full_text: str, threshold: float = None) -> bool:
    """
    Verify that a quote actually appears in the source text.

    Uses multi-layer validation:
    1. Exact substring match (fast path)
    2. Exact n-gram anchor match (requires 8+ word exact sequence)
    3. Fuzzy sliding window (fallback with high threshold)
    """
    if threshold is None:
        threshold = CITATION_FUZZY_MATCH_THRESHOLD

    quote_norm = " ".join(quote.lower().split())
    text_norm = " ".join(full_text.lower().split())

    # Layer 1: Exact substring match
    if quote_norm in text_norm:
        return True

    # Layer 2: Require at least one exact 8-word sequence match
    quote_words = quote_norm.split()
    text_words = text_norm.split()

    if len(quote_words) >= 8:
        has_anchor = False
        for i in range(len(quote_words) - 7):
            anchor = " ".join(quote_words[i:i+8])
            if anchor in text_norm:
                has_anchor = True
                break

        if not has_anchor:
            return False

    # Layer 3: Fuzzy sliding window match
    window_size = len(quote_words)

    for i in range(len(text_words) - window_size + 1):
        window = " ".join(text_words[i:i + window_size])
        ratio = SequenceMatcher(None, quote_norm, window).ratio()
        if ratio >= threshold:
            return True

    return False

def extract_numeric_anchors(text: str) -> set:
    """Extract numeric anchors from text for validation."""
    import re
    patterns = [
        r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|trillion|B|M|T))?',
        r'\d+(?:\.\d+)?%',
        r'\b(?:19|20)\d{2}\b',
        r'\b(?:Q[1-4])\b',
    ]
    anchors = set()
    for pattern in patterns:
        anchors.update(re.findall(pattern, text, re.IGNORECASE))
    return anchors

def validate_citation_anchors(quote: str, full_text: str) -> bool:
    """Verify that numeric anchors in the quote exist in the source."""
    quote_anchors = extract_numeric_anchors(quote)

    if not quote_anchors:
        return True

    text_anchors = extract_numeric_anchors(full_text)
    return quote_anchors.issubset(text_anchors)

def validate_citations(
    citations: List[dict],
    articles: List
) -> Tuple[List[Citation], int]:
    """Validate that citations actually appear in source articles."""
    url_to_article = {a.url: a for a in articles}

    valid_citations = []
    rejected = 0

    for cit in citations:
        url = cit.get("url", "")
        quote = cit.get("quote", "")

        article = url_to_article.get(url)
        if not article:
            rejected += 1
            continue

        full_text = (article.full_text or "") + " " + article.summary

        if not fuzzy_quote_match(quote, full_text):
            rejected += 1
            continue

        if not validate_citation_anchors(quote, full_text):
            rejected += 1
            continue

        valid_citations.append(Citation(
            article_title=cit.get("article_title", article.title),
            quote=quote,
            url=url,
            source=article.source,
            published_date=article.published_date,
            is_verified=True
        ))

    return valid_citations, rejected

def extract_theme_from_cluster(cluster: Cluster) -> Theme:
    """Extract an investment theme from a cluster of articles."""
    articles_formatted = format_articles_for_prompt(cluster.articles)

    prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(
        count=len(cluster.articles),
        publisher_count=cluster.unique_publishers,
        centroid=cluster.centroid_text,
        articles_formatted=articles_formatted
    )}"

    response = send_analysis_request(prompt)

    theme_data = response.get("theme", {})

    raw_citations = theme_data.get("citations", [])
    valid_citations, rejected = validate_citations(
        raw_citations,
        cluster.articles
    )

    theme = Theme(
        theme_name=theme_data.get("theme_name", "Unknown Theme"),
        industries=theme_data.get("industries", []),
        reasoning=theme_data.get("reasoning", ""),
        citations=valid_citations,
        confidence=theme_data.get("confidence", "LOW"),
        sentiment=theme_data.get("sentiment", "NEUTRAL"),
    )

    return theme
```

### 11. Confidence Scorer (`src/synthesis/confidence_scorer.py`)

```python
"""
Calculate and enforce confidence scores for themes.

CRITICAL: This module enforces source diversity rules that the LLM might not follow.
"""
from typing import List
from datetime import datetime, timedelta
from src.models import Theme, Citation
from config.settings import TIER_1_SOURCES

def calculate_confidence_score(theme: Theme) -> float:
    """Calculate numeric confidence score (0-100) based on citation quality."""
    if not theme.citations:
        return 0.0

    score = 0.0
    citations = theme.citations

    # Citation count: +15 each, max 60
    score += min(len(citations) * 15, 60)

    # Source diversity
    unique_sources = get_unique_sources(citations)
    if len(unique_sources) >= 3:
        score += 20
    elif len(unique_sources) == 2:
        score += 10

    # Tier-1 source bonus
    tier1_count = sum(1 for c in citations if c.source in TIER_1_SOURCES)
    score += min(tier1_count * 10, 20)

    # Recency bonus
    now = datetime.utcnow()
    recent_count = sum(
        1 for c in citations
        if (now - c.published_date) < timedelta(hours=6)
    )
    if recent_count >= 2:
        score += 10

    return min(score, 100.0)

def get_unique_sources(citations: List[Citation]) -> set:
    """Get unique source names from citations."""
    return set(c.source for c in citations)

def get_tier1_count(citations: List[Citation]) -> int:
    """Count citations from tier-1 sources."""
    return sum(1 for c in citations if c.source in TIER_1_SOURCES)

def enforce_confidence_level(theme: Theme) -> Theme:
    """
    Enforce confidence level based on source diversity rules.

    This OVERRIDES the LLM's confidence rating if it doesn't meet
    our hard rules for source diversity.
    """
    if not theme.citations:
        theme.confidence = "LOW"
        theme.confidence_score = 0.0
        return theme

    unique_sources = get_unique_sources(theme.citations)
    tier1_count = get_tier1_count(theme.citations)

    theme.confidence_score = calculate_confidence_score(theme)

    if len(unique_sources) >= 3 and tier1_count >= 1:
        pass  # Allow HIGH
    elif len(unique_sources) >= 2:
        if theme.confidence == "HIGH":
            theme.confidence = "MEDIUM"
    else:
        theme.confidence = "LOW"

    if theme.confidence_score < 50 and theme.confidence == "HIGH":
        theme.confidence = "MEDIUM"
    if theme.confidence_score < 30:
        theme.confidence = "LOW"

    return theme

def calculate_scores(themes: List[Theme]) -> List[Theme]:
    """Calculate and enforce confidence for all themes."""
    scored_themes = []

    for theme in themes:
        theme = enforce_confidence_level(theme)
        scored_themes.append(theme)

    scored_themes.sort(key=lambda t: t.confidence_score, reverse=True)

    return scored_themes
```

### 12. Low Signal Day Detection

```python
"""
Detect and flag low-signal days.

A low-signal day occurs when the input data quality is insufficient
to produce reliable theme analysis. Rather than output noise,
we explicitly flag these conditions.

Location: src/synthesis/signal_detector.py
"""
from typing import List, Tuple
from src.models import Article, Cluster, ContentMode
from config.settings import (
    LOW_SIGNAL_CLUSTERS_THRESHOLD,
    LOW_SIGNAL_SUMMARY_ONLY_RATIO
)

def detect_low_signal_day(
    articles: List[Article],
    clusters: List[Cluster]
) -> Tuple[bool, List[str]]:
    """
    Detect if this is a low-signal day.

    Returns:
        Tuple of (is_low_signal: bool, reasons: List[str])
    """
    reasons = []

    # Check 1: Too few clusters passed quality filters
    if len(clusters) < LOW_SIGNAL_CLUSTERS_THRESHOLD:
        reasons.append(
            f"Only {len(clusters)} clusters passed filters "
            f"(min: {LOW_SIGNAL_CLUSTERS_THRESHOLD})"
        )

    # Check 2: Too many summary-only articles (paywall fallback)
    if articles:
        summary_only_count = sum(
            1 for a in articles
            if a.content_mode == ContentMode.SUMMARY_ONLY
        )
        summary_ratio = summary_only_count / len(articles)

        if summary_ratio > LOW_SIGNAL_SUMMARY_ONLY_RATIO:
            reasons.append(
                f"{summary_ratio:.0%} of articles are summary-only "
                f"(max: {LOW_SIGNAL_SUMMARY_ONLY_RATIO:.0%})"
            )

    # Check 3: Low source diversity in final clusters
    if clusters:
        all_sources = set()
        for cluster in clusters:
            for article in cluster.articles:
                all_sources.add(article.source)

        if len(all_sources) < 3:
            reasons.append(
                f"Only {len(all_sources)} unique sources across all clusters"
            )

    return len(reasons) > 0, reasons
```

### 13. CLI Entry Point (`main.py`)

```python
#!/usr/bin/env python3
"""
Financial News Theme Analysis Tool - CLI Entry Point.

Two modes of operation:
1. Collector mode (--collector): Hourly RSS polling, stores to SQLite, no LLM
2. Analyzer mode (--run-eod): EOD analysis with LLM theme extraction
"""
import argparse
import sys
import time
import json
from datetime import datetime, timedelta
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.settings import (
    LOOKBACK_HOURS_EOD,
    LOOKBACK_HOURS_COLLECTOR,
    TARGET_SELECTED_ARTICLES,
    CANDIDATE_POOL_SIZE,
    KST
)
from src.models import (
    AnalysisResult, Theme, Article,
    CollectorRunStats, AnalyzerRunStats, TruncationWarning
)
from src.ingestion.rss_fetcher import fetch_all_feeds, detect_truncation_risks
from src.ingestion.article_extractor import extract_articles_content
from src.processing.article_parser import parse_and_validate
from src.processing.deduplicator import deduplicate_articles
from src.processing.clustering import cluster_articles
from src.selection.info_density import score_articles
from src.selection.candidate_pruner import prune_candidates, get_pruning_stats
from src.selection.card_selector import select_articles
from src.analysis.theme_extractor import extract_theme_from_cluster
from src.analysis.gemini_client import estimate_cost
from src.synthesis.theme_aggregator import aggregate_themes
from src.synthesis.confidence_scorer import calculate_scores
from src.synthesis.signal_detector import detect_low_signal_day
from src.storage.db import (
    init_db,
    insert_article,
    get_articles_in_window,
    upsert_theme,
    determine_trend_status,
    save_collector_run,
    save_analyzer_run,
    article_exists
)
from src.presentation.terminal_formatter import print_full_report, print_low_signal_warning
from src.presentation.report_generator import save_text_report, save_json_report

console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze financial news to identify investment themes."
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--collector",
        action="store_true",
        help="Run collector mode: fetch RSS and store articles (no LLM)"
    )
    mode_group.add_argument(
        "--run-eod",
        action="store_true",
        help="Run EOD analyzer: select articles, cluster, extract themes"
    )

    # Common options
    parser.add_argument(
        "--sources",
        nargs="+",
        help="Specific sources to analyze (e.g., bloomberg cnbc)"
    )
    parser.add_argument(
        "--all-sources",
        action="store_true",
        default=True,
        help="Use all configured sources (default)"
    )

    # Analyzer options
    parser.add_argument(
        "--hours",
        type=int,
        default=LOOKBACK_HOURS_EOD,
        help=f"Lookback window in hours for EOD analysis (default: {LOOKBACK_HOURS_EOD})"
    )
    parser.add_argument(
        "--target-articles",
        type=int,
        default=TARGET_SELECTED_ARTICLES,
        help=f"Target number of articles to analyze (default: {TARGET_SELECTED_ARTICLES})"
    )
    parser.add_argument(
        "--skip-selection",
        action="store_true",
        help="Skip LLM selection stage (use deterministic pruning only)"
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=50,
        help="Minimum confidence score to display (default: 50)"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        help="Save text report to file"
    )
    parser.add_argument(
        "--export-json",
        type=str,
        help="Export results to JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()

def run_collector(args) -> CollectorRunStats:
    """
    Run collector mode: fetch RSS feeds and store to SQLite.

    This mode runs frequently (e.g., hourly) and does NOT call any LLM.
    Its purpose is to capture as many articles as RSS exposes before
    they get evicted from the feed.
    """
    start_time = time.time()
    init_db()

    cutoff_time = datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS_COLLECTOR)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Step 1: Fetch RSS feeds
        task = progress.add_task("Fetching RSS feeds...", total=None)
        articles, truncation_warnings = fetch_all_feeds(
            sources=args.sources,
            cutoff_time=cutoff_time,
            all_sources=args.all_sources,
            detect_truncation=True
        )
        progress.update(task, completed=True)
        console.print(f"  → Fetched {len(articles)} articles from feeds")

        # Step 2: Extract content
        task = progress.add_task("Extracting article content...", total=None)
        articles = extract_articles_content(articles)
        progress.update(task, completed=True)

        # Step 3: Parse and validate
        task = progress.add_task("Parsing and validating...", total=None)
        articles = parse_and_validate(articles)
        progress.update(task, completed=True)

        # Step 4: Store new articles
        task = progress.add_task("Storing to database...", total=None)
        new_count = 0
        dupe_count = 0

        for article in articles:
            if article_exists(article.guid, article.source):
                dupe_count += 1
            else:
                insert_article(article)
                new_count += 1

        progress.update(task, completed=True)
        console.print(f"  → Stored {new_count} new articles, skipped {dupe_count} duplicates")

    elapsed = time.time() - start_time

    # Log truncation warnings
    for warning in truncation_warnings:
        console.print(f"[yellow]⚠ TRUNCATION RISK: {warning.source}[/yellow]")
        console.print(f"    {warning.recommendation}")

    stats = CollectorRunStats(
        run_id=0,  # Set by DB
        run_timestamp=datetime.utcnow(),
        sources_fetched=len(set(a.source for a in articles)),
        entries_found=len(articles),
        new_articles_stored=new_count,
        duplicates_skipped=dupe_count,
        truncation_warnings=truncation_warnings,
        duration_seconds=elapsed
    )

    stats.run_id = save_collector_run(stats)

    console.print(f"\n[green]Collector run complete in {elapsed:.1f}s[/green]")

    return stats

def run_analyzer(args) -> Optional[AnalysisResult]:
    """
    Run EOD analyzer mode: select articles, cluster, extract themes.

    This mode runs once per day (e.g., 23:30 KST) and makes LLM calls.
    It queries SQLite for all articles in the lookback window.
    """
    start_time = time.time()
    init_db()

    api_calls = 0
    total_input_tokens = 0
    total_output_tokens = 0

    run_date = datetime.now(KST).strftime("%Y-%m-%d")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Step 1: Query articles from database
        task = progress.add_task("Querying stored articles...", total=None)
        articles = get_articles_in_window(args.hours)
        progress.update(task, completed=True)
        collected_count = len(articles)
        console.print(f"  → Found {collected_count} articles in last {args.hours}h")

        if not articles:
            console.print("[yellow]No articles found in lookback window.[/yellow]")
            return None

        # Step 2: Deduplicate by content
        task = progress.add_task("Deduplicating articles...", total=None)
        articles = deduplicate_articles(articles)
        progress.update(task, completed=True)
        unique_count = len(articles)
        console.print(f"  → {unique_count} unique articles after deduplication")

        # Step 3: Score articles by info density
        task = progress.add_task("Scoring article quality...", total=None)
        articles = score_articles(articles)
        progress.update(task, completed=True)

        # Step 4: Deterministic pruning
        task = progress.add_task("Pruning low-quality articles...", total=None)
        candidates = prune_candidates(articles)
        pruning_stats = get_pruning_stats(articles, candidates)
        progress.update(task, completed=True)
        candidate_count = len(candidates)
        console.print(f"  → {candidate_count} candidates after quality pruning")

        # Step 5: LLM-based selection (optional)
        if not args.skip_selection and len(candidates) > args.target_articles:
            task = progress.add_task("Selecting articles (LLM)...", total=None)
            # Note: In production, we'd pass article IDs from database
            # For now, use index as placeholder
            article_ids = list(range(len(candidates)))
            selected_ids = select_articles(candidates, article_ids)
            selected_articles = [candidates[i] for i in selected_ids if i < len(candidates)]
            api_calls += 1
            total_input_tokens += 5000  # Approximate card selection cost
            total_output_tokens += 500
            progress.update(task, completed=True)
            console.print(f"  → Selected {len(selected_articles)} articles for analysis")
        else:
            selected_articles = candidates[:args.target_articles]
            console.print(f"  → Using top {len(selected_articles)} candidates (no LLM selection)")

        selected_count = len(selected_articles)

        # Calculate summary-only ratio
        summary_only_count = sum(
            1 for a in selected_articles
            if a.content_mode.value == "summary"
        )
        summary_only_ratio = summary_only_count / max(selected_count, 1)

        # Step 6: Cluster selected articles
        task = progress.add_task("Clustering articles...", total=None)
        clusters = cluster_articles(selected_articles)
        progress.update(task, completed=True)
        console.print(f"  → Created {len(clusters)} valid clusters")

        if not clusters:
            console.print("[yellow]No significant clusters found.[/yellow]")
            return None

        # Step 7: Check for low signal day
        is_low_signal, low_signal_reasons = detect_low_signal_day(
            selected_articles, clusters
        )

        if is_low_signal:
            print_low_signal_warning(low_signal_reasons)

        # Step 8: Extract themes from each cluster
        themes: List[Theme] = []
        for i, cluster in enumerate(clusters):
            task = progress.add_task(
                f"Analyzing cluster {i+1}/{len(clusters)}...",
                total=None
            )
            try:
                theme = extract_theme_from_cluster(cluster)
                themes.append(theme)
                api_calls += 1
                total_input_tokens += cluster.estimated_tokens
                total_output_tokens += 1000
            except Exception as e:
                console.print(f"[red]Error analyzing cluster {i+1}: {e}[/red]")
            progress.update(task, completed=True)

        # Step 9: Aggregate and score themes
        task = progress.add_task("Aggregating themes...", total=None)
        themes = aggregate_themes(themes)
        themes = calculate_scores(themes)
        progress.update(task, completed=True)

        # Step 10: Filter by minimum confidence
        themes = [t for t in themes if t.confidence_score >= args.min_confidence]
        themes.sort(key=lambda t: t.confidence_score, reverse=True)

        # Step 11: Persist to database
        task = progress.add_task("Updating theme database...", total=None)
        for theme in themes:
            theme.trend_status = determine_trend_status(theme.theme_name)
            upsert_theme(theme)
        progress.update(task, completed=True)

    elapsed = time.time() - start_time
    estimated_cost = estimate_cost(total_input_tokens, total_output_tokens)

    # Build stats
    stats = AnalyzerRunStats(
        run_id=0,
        run_date=run_date,
        run_timestamp=datetime.utcnow(),
        lookback_hours=args.hours,
        collected_count=collected_count,
        unique_count=unique_count,
        candidate_count=candidate_count,
        selected_count=selected_count,
        summary_only_ratio=summary_only_ratio,
        cluster_count=len(clusters),
        themes_extracted=len(themes),
        llm_calls=api_calls,
        token_usage_input=total_input_tokens,
        token_usage_output=total_output_tokens,
        estimated_cost_usd=estimated_cost,
        is_low_signal_day=is_low_signal,
        low_signal_reasons=low_signal_reasons,
        processing_time_seconds=elapsed
    )

    stats.run_id = save_analyzer_run(stats)

    return AnalysisResult(
        stats=stats,
        themes=themes,
        truncation_warnings=[]  # Populated by collector, not analyzer
    )

def main():
    """Main entry point."""
    args = parse_args()

    try:
        if args.collector:
            run_collector(args)
        elif args.run_eod:
            result = run_analyzer(args)

            if result is None:
                sys.exit(1)

            # Display results
            print_full_report(result)

            # Export if requested
            if args.output:
                save_text_report(result, args.output)
                console.print(f"\n[green]Text report saved to: {args.output}[/green]")

            if args.export_json:
                save_json_report(result, args.export_json)
                console.print(f"[green]JSON export saved to: {args.export_json}[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Dependencies

### `requirements.txt`

```
# ============================================================================
# Financial News Theme Analysis Tool - Dependencies
# ============================================================================
#
# WINDOWS USERS: Do NOT run `pip install -r requirements.txt` directly!
# Use the setup script instead: .\scripts\setup.ps1
#
# This ensures CPU-only PyTorch is installed first (150MB vs 2.5GB).
# ============================================================================

# AI Engine
google-genai>=1.0.0           # Gemini 3 Flash API (new SDK)

# Response Validation
pydantic>=2.5.0               # JSON schema validation for API responses

# RSS & Web Scraping
feedparser>=6.0.10            # RSS parsing
requests>=2.31.0              # HTTP requests
trafilatura>=1.8.0            # Article extraction

# Clustering & Vectorization
# NOTE: torch must be installed separately on Windows (see setup script)
sentence-transformers>=2.2.2  # all-MiniLM-L6-v2 embeddings
scikit-learn>=1.3.0           # AgglomerativeClustering
numpy>=1.24.0                 # Numerical operations

# Data Processing
python-dateutil>=2.8.2        # Date parsing

# Terminal UI
rich>=13.7.0                  # Bloomberg-style output
colorama>=0.4.6               # Cross-platform colors

# Utilities
python-dotenv>=1.0.0          # Environment variables
tenacity>=8.2.3               # Retry logic with backoff

# Storage (sqlite3 is built-in)
```

---

## Environment Setup (`.env.example`)

```bash
# Gemini API Key (required)
# Get from: https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_api_key_here

# Optional: Override default settings
# GEMINI_MODEL=gemini-3-flash-preview
# LOOKBACK_HOURS_EOD=28
# TARGET_SELECTED_ARTICLES=80
# POLL_INTERVAL_MINUTES=60
```

---

## Implementation Phases

### Phase 1: Foundation
1. Create directory structure with `__init__.py` files
2. Create `requirements.txt` (with Windows PyTorch note)
3. Create `scripts/setup.ps1` (Windows PowerShell)
4. Create `.env.example` and `.gitignore`
5. Setup virtual environment (run setup script)
6. Implement `config/settings.py`
7. Create `config/rss_sources.json`
8. Implement `utils/logger.py`
9. Implement `utils/rate_limiter.py`

### Phase 2: Storage Layer
10. Implement `src/storage/db.py` with full schema
11. Create `src/models.py` with all dataclasses

### Phase 3: Ingestion (Collector Mode)
12. Implement `src/ingestion/rss_fetcher.py` with truncation detection
13. Implement `src/ingestion/article_extractor.py`

### Phase 4: Processing
14. Implement `src/processing/article_parser.py`
15. Implement `src/processing/deduplicator.py`
16. Implement `src/processing/clustering.py` with publisher diversity

### Phase 5: Selection Stage (NEW)
17. Implement `src/selection/info_density.py`
18. Implement `src/selection/candidate_pruner.py`
19. Implement `src/selection/card_selector.py`

### Phase 6: Analysis
20. Implement `src/analysis/gemini_client.py`
21. Implement `src/analysis/theme_extractor.py`

### Phase 7: Synthesis
22. Implement `src/synthesis/theme_aggregator.py`
23. Implement `src/synthesis/confidence_scorer.py`
24. Implement `src/synthesis/signal_detector.py`

### Phase 8: Presentation
25. Implement `src/presentation/terminal_formatter.py`
26. Implement `src/presentation/report_generator.py`

### Phase 9: Integration
27. Implement `main.py` with dual-mode CLI
28. Create `scripts/schedule_collector.ps1`
29. End-to-end testing
30. Write `README.md`

---

## CLI Usage Examples

```bash
# COLLECTOR MODE (run hourly, no LLM cost)
python main.py --collector

# EOD ANALYZER MODE (run once at end of day)
python main.py --run-eod

# Analyzer with custom lookback window
python main.py --run-eod --hours 36

# Analyzer with fewer articles (faster/cheaper)
python main.py --run-eod --target-articles 50

# Skip LLM selection (deterministic only)
python main.py --run-eod --skip-selection

# High confidence only, save report
python main.py --run-eod --min-confidence 70 --output report.txt

# Export JSON for downstream processing
python main.py --run-eod --export-json themes.json

# Verbose mode for debugging
python main.py --run-eod --verbose
```

---

## Critical Success Factors

### 1. Coverage: Avoid Feed Eviction
- Run collector every 30-60 minutes
- Monitor truncation warnings
- Add supplementary feeds for gaps

### 2. Quality: Avoid Trash Sampling
- Info-density scoring filters fluff
- Card-based selection focuses on relevance
- Low-signal-day detection prevents false confidence

### 3. Reliability: Citation Validation
- Multi-layer fuzzy matching
- Numeric anchor verification
- Source diversity enforcement

### 4. Cost Control: Bounded LLM Spend
- Collector mode: $0 (no LLM)
- Selection stage: ~$0.01 (one call)
- Theme extraction: ~$0.08 (5-8 calls)
- Total: ~$0.10/day

---

## Ready to Implement

This plan incorporates:
- Decoupled collector/analyzer architecture
- Greedy collection with bounded analysis
- Deterministic pruning + LLM selection
- Feed truncation risk detection
- Low-signal-day warnings
- Expanded SQLite schema for articles and runs
- Publisher diversity enforcement in clustering
- Time concentration limits in selection

**Estimated Implementation Time**: 5-7 days
**Estimated Monthly Cost**: ~$3.00 (daily EOD runs)
