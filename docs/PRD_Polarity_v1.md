# Product Requirements Document: Polarity

**Version:** 1.0
**Last Updated:** December 29, 2025
**Status:** Draft - Pending Stakeholder Approval
**Author:** [Consultant/PM]
**Stakeholder:** [Client]

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [User Persona](#3-user-persona)
4. [Product Vision](#4-product-vision)
5. [Feature Requirements](#5-feature-requirements)
6. [Technical Architecture](#6-technical-architecture)
7. [UI/UX Requirements](#7-uiux-requirements)
8. [Data Strategy](#8-data-strategy)
9. [AI/ML Strategy](#9-aiml-strategy)
10. [Success Metrics](#10-success-metrics)
11. [Risks & Mitigations](#11-risks--mitigations)
12. [Out of Scope](#12-out-of-scope)
13. [Open Questions](#13-open-questions)
14. [Appendix](#14-appendix)

---

## 1. Executive Summary

### 1.1 Product Name
**Polarity** — Named for its core capability: measuring the alignment (or divergence) between a portfolio's exposure and the market's thematic direction.

### 1.2 One-Line Description
A Bloomberg Terminal-inspired web platform that aggregates financial news, identifies emerging investment themes using AI, and provides an interactive research environment for position traders and long-term investors.

### 1.3 Core Value Proposition
Polarity transforms thousands of daily financial news articles into actionable thematic intelligence, enabling investors to:
- **Identify** emerging market themes before they become mainstream
- **Understand** the underlying drivers through AI-assisted dialogue
- **Validate** investment decisions against thematic alignment

### 1.4 Target User
Individual position trader / long-term investor managing a personal portfolio across global equities, ETFs, commodities, and major cryptocurrencies.

### 1.5 Key Differentiators
| Traditional Approach | Polarity |
|---------------------|----------|
| Manual news reading (hours/day) | AI-curated daily highlights + weekly themes |
| Scattered research across platforms | Unified terminal with contextual chat |
| Gut-feel investment alignment | Quantified theme-exposure alignment scoring |
| Single AI model responses | Multi-model debate for complex questions |

---

## 2. Problem Statement

### 2.1 The Challenge
Modern financial markets generate an overwhelming volume of information:
- **Volume:** 1,000+ financial news articles published daily across major sources
- **Velocity:** Market-moving information can emerge and be priced in within hours
- **Complexity:** Interconnected global themes (geopolitics, supply chains, monetary policy) require synthesized understanding

### 2.2 Current Pain Points

| Pain Point | Impact |
|------------|--------|
| **Information Overload** | Impossible to read and process all relevant news manually |
| **Theme Identification Lag** | By the time a theme is obvious, the market has already moved |
| **Confirmation Bias** | Self-directed research tends to reinforce existing beliefs |
| **Scattered Tooling** | Research spread across news sites, brokerages, and chat interfaces |
| **No Historical Context** | Difficult to track how themes evolve over weeks/months |

### 2.3 The Opportunity
Large Language Models can now:
- Process and summarize vast quantities of text
- Identify semantic clusters across disparate sources
- Engage in educational dialogue with citations
- Challenge assumptions and stress-test investment theses

Polarity harnesses these capabilities within a purpose-built investment research interface.

---

## 3. User Persona

### 3.1 Primary Persona: The Position Trader

**Name:** Alex (representative persona)
**Role:** Individual investor managing personal portfolio
**Experience:** Intermediate to advanced financial literacy

#### Investment Profile
| Attribute | Value |
|-----------|-------|
| Holding Period | 6 months to 1+ years |
| Decision Frequency | Weekly to monthly |
| Portfolio Size | Personal capital |
| Risk Tolerance | Moderate |

#### Asset Classes Traded
- Individual stocks (global markets)
- Exchange-Traded Funds (ETFs)
- Commodities
- Cryptocurrencies (BTC, ETH only)
- Bonds (rare)

#### Goals
1. **Time Efficiency:** Reduce daily research time from 2+ hours to <30 minutes
2. **Early Theme Detection:** Identify emerging themes 1-2 weeks before mainstream recognition
3. **Decision Quality:** Eliminate confirmation bias through structured validation
4. **Continuous Learning:** Deepen understanding of market mechanisms through AI dialogue

#### Frustrations
- "I can't read everything. I know I'm missing important signals."
- "By the time I see a theme on CNBC, it's already priced in."
- "I make decisions, but I'm never sure if I'm just confirming what I wanted to believe."
- "I want to understand *why* something is happening, not just *what* is happening."

---

## 4. Product Vision

### 4.1 Vision Statement
Polarity will be the definitive personal investment research terminal — combining the information density of Bloomberg with the analytical depth of a quantitative research team and the educational engagement of a personal tutor.

### 4.2 Design Philosophy

#### 4.2.1 Bloomberg Terminal Aesthetic
The platform explicitly rejects modern minimalist UI trends in favor of:
- **High-density layouts:** Maximum data per screen
- **Tiled pane architecture:** Multiple information streams visible simultaneously
- **Monospace typography:** Terminal-style readability
- **Keyboard-centric navigation:** Power-user efficiency

#### 4.2.2 Manual-First Control
The user retains full control over:
- Resource allocation (when to trigger expensive AI operations)
- Portfolio decisions (no automated trading)
- Data persistence (what to save, what to discard)

#### 4.2.3 Traceable Intelligence
Every AI-generated insight must be:
- Linked to source articles
- Flagged when synthesizing beyond available citations
- Auditable through cascading reference drill-down

### 4.3 Core Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           POLARITY CORE WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   COLLECT    │     │   ANALYZE    │     │   RESEARCH   │
    │   (Daily)    │────▶│   (Weekly)   │────▶│   (On-Demand)│
    └──────────────┘     └──────────────┘     └──────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │ RSS Fetching │     │Theme Cluster │     │ Contextual   │
    │ Key News     │     │ Analysis     │     │ Chat + Q&A   │
    │ Highlights   │     │ Ticker/ETF   │     │ Deep Dive    │
    │              │     │ Suggestions  │     │ Multi-Model  │
    └──────────────┘     └──────────────┘     └──────────────┘
                                                    │
                                                    ▼
                               ┌──────────────────────────────┐
                               │       DECISION AUDIT         │
                               │  (Validate Against Themes)   │
                               └──────────────────────────────┘
```

**Stage 1: Collect (Daily)**
- Automated RSS polling every 30-60 minutes
- No LLM calls (zero cost)
- Key news highlighting based on deterministic scoring
- Storage to Supabase for historical tracking

**Stage 2: Analyze (Weekly)**
- Theme clustering using embeddings + LLM synthesis
- Confidence scoring and sentiment classification
- Ticker/ETF mapping to actionable instruments
- Trend tracking (NEW → STABLE → FADING)

**Stage 3: Research (On-Demand)**
- Contextual chat with current theme context
- Single-model default (Gemini 3 Flash)
- Multi-model debate for complex questions (manual trigger)
- Educational explanations with metaphors and citations

**Stage 4: Decision Audit (Post-Research)**
- User submits investment decision
- System stress-tests against theme alignment
- Red/Green flag with divergence scoring

---

## 5. Feature Requirements

### 5.1 Feature Prioritization Matrix

| Priority | Feature | Description | Phase |
|----------|---------|-------------|-------|
| P1 | Daily Key News Highlights | Automated collection + deterministic highlighting | MVP |
| P1 | Weekly Theme Clustering | AI-powered theme identification and grouping | MVP |
| P1 | Cascading Source References | Drill-down to original articles with hyperlinks | MVP |
| P1 | Contextual Chat (Single Model) | Theme-aware Q&A using Gemini 3 Flash | MVP |
| P1 | Ticker/ETF Suggestions | Map themes to tradeable instruments | MVP |
| P2 | Multi-Model Deep Analysis | GPT + Gemini + Claude debate (manual trigger) | Phase 2 |
| P2 | API Cost Dashboard | Real-time usage and budget tracking | Phase 2 |
| P3 | Decision Audit | Stress-test user conclusions against themes | Phase 3 |
| P4 | Exposure Recording + Alignment | Manual portfolio entry with Red/Green flags | Phase 4 |

### 5.2 Detailed Feature Specifications

#### 5.2.1 [P1] Daily Key News Highlights

**Purpose:** Surface the most significant news articles without requiring full analysis.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| DH-01 | System shall fetch RSS feeds from configured sources every 60 minutes |
| DH-02 | System shall deduplicate articles by URL and content hash |
| DH-03 | System shall compute info-density score for each article |
| DH-04 | System shall highlight top N articles per day based on composite scoring |
| DH-05 | Highlighted articles shall display: title, source, time, summary snippet |
| DH-06 | User shall be able to filter highlights by source, time range, or keyword |

**Info-Density Scoring Factors:**
- Numeric data density (percentages, dollar amounts, statistics)
- Named entity concentration (companies, tickers, people)
- Causal language presence ("caused by", "resulted in", "due to")
- Negative signals: opinion indicators, listicle patterns, promotional language

**"Key News" Definition:**
An article is considered "key" if it scores in the top 20% of info-density AND:
- Comes from a Tier 1 source, OR
- Is corroborated by 2+ sources within 6 hours, OR
- Contains named entities matching user's watchlist (future enhancement)

---

#### 5.2.2 [P1] Weekly Theme Clustering + Analysis

**Purpose:** Identify and synthesize emerging investment themes from collected articles.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| TC-01 | System shall run theme analysis on a configurable schedule (default: weekly) |
| TC-02 | Analysis shall consider all articles from the lookback window (default: 7 days) |
| TC-03 | System shall generate vector embeddings for article content |
| TC-04 | System shall cluster articles using agglomerative clustering |
| TC-05 | Each cluster shall require minimum 3 articles from 2+ unique publishers |
| TC-06 | System shall generate theme summary via LLM for each valid cluster |
| TC-07 | Theme summary shall include: name, sentiment, confidence, reasoning |
| TC-08 | System shall track theme lifecycle: NEW → STABLE → FADING |
| TC-09 | Theme history shall be persisted for longitudinal analysis |

**Theme Output Schema:**
```
Theme:
  - name: string (e.g., "Semiconductor Capex Slowdown")
  - sentiment: BULLISH | BEARISH | NEUTRAL
  - confidence: HIGH | MEDIUM | LOW
  - confidence_score: float (0-100)
  - industries: string[] (GICS sectors)
  - reasoning: string (2-3 sentence investment thesis)
  - citations: Citation[]
  - first_detected: datetime
  - last_updated: datetime
  - mention_count: int
  - trend_status: NEW | STABLE | FADING
```

---

#### 5.2.3 [P1] Cascading Source References

**Purpose:** Provide full traceability from theme insights to original source articles.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| CR-01 | Each theme shall display supporting citations |
| CR-02 | Citations shall include: article title, source, date, verbatim quote |
| CR-03 | Clicking a citation shall expand inline to show full context |
| CR-04 | Each citation shall include hyperlink to original article |
| CR-05 | Expansion shall not cause layout shift in parent container |
| CR-06 | Citations shall be validated via fuzzy matching against source text |
| CR-07 | Unverified citations shall be flagged with warning indicator |

**UI Behavior:**
- Default: Show theme summary + 2-3 key citations collapsed
- Click to expand: Reveal all citations in scrollable pane
- Fixed-width container prevents layout disruption
- Hyperlinks open in new tab

---

#### 5.2.4 [P1] Contextual Chat (Single Model)

**Purpose:** Enable interactive Q&A about themes with full context awareness.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| CC-01 | Chat panel shall be integrated into main terminal interface |
| CC-02 | Chat shall automatically receive context of currently viewed theme |
| CC-03 | Default model shall be Gemini 3 Flash |
| CC-04 | Responses shall include citations where applicable |
| CC-05 | Responses shall flag when synthesizing beyond available sources |
| CC-06 | Chat history shall persist within session |
| CC-07 | User shall be able to clear context and start fresh |
| CC-08 | Response latency shall be <5 seconds for typical queries |

**Context Injection:**
When user views a theme, the chat system prompt includes:
- Theme summary and reasoning
- All supporting citations (full text)
- Related articles from the same cluster
- User's previous questions in this session

**Citation Flagging:**
Responses must distinguish:
- `[Cited]` - Claim directly supported by source article
- `[Synthesized]` - Claim inferred from multiple sources
- `[General Knowledge]` - Claim from model training, no article support

---

#### 5.2.5 [P1] Ticker/ETF Suggestions

**Purpose:** Map abstract themes to concrete tradeable instruments.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| TE-01 | Each theme shall suggest relevant tickers and ETFs |
| TE-02 | Suggestions shall include: symbol, name, relevance explanation |
| TE-03 | Suggestions shall distinguish direct vs. indirect exposure |
| TE-04 | System shall not provide buy/sell recommendations |
| TE-05 | Suggestions shall be generated via LLM with citation requirements |
| TE-06 | User shall be able to dismiss irrelevant suggestions |

**Suggestion Schema:**
```
Suggestion:
  - symbol: string (e.g., "NVDA", "SMH")
  - name: string (e.g., "NVIDIA Corporation")
  - type: STOCK | ETF | CRYPTO
  - exposure_type: DIRECT | INDIRECT
  - relevance: string (explanation of connection to theme)
  - mentioned_in_sources: boolean
```

**Direct vs. Indirect:**
- Direct: Company explicitly mentioned in theme articles
- Indirect: Company has structural exposure to theme (e.g., TSMC for semiconductor theme even if not named)

---

#### 5.2.6 [P2] Multi-Model Deep Analysis

**Purpose:** Provide higher-confidence answers for complex questions through model consensus.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| MD-01 | User shall manually trigger deep analysis via explicit command |
| MD-02 | Deep analysis shall query 3 models: GPT, Gemini, Claude |
| MD-03 | System shall synthesize responses into consensus view |
| MD-04 | Divergent opinions shall be explicitly highlighted |
| MD-05 | Cost estimate shall be shown before execution |
| MD-06 | User shall confirm cost before proceeding |

**Consensus Algorithm:**
1. Query all 3 models with identical prompt + context
2. Extract key claims from each response
3. Identify agreement (2/3 or 3/3 models concur)
4. Highlight disagreements with model attribution
5. Present unified response with confidence indicator

**Cost Display:**
```
Deep Analysis Cost Estimate:
  - GPT-4.5:    ~$0.15
  - Gemini:     ~$0.02
  - Claude:     ~$0.45
  - Total:      ~$0.62

  [Confirm] [Cancel]
```

---

#### 5.2.7 [P2] API Cost Dashboard

**Purpose:** Provide transparency into AI usage and budget management.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| AC-01 | Dashboard shall display real-time token usage per model |
| AC-02 | Dashboard shall show estimated cost (today, MTD, total) |
| AC-03 | User shall be able to set monthly budget limit |
| AC-04 | System shall warn when approaching budget threshold (80%) |
| AC-05 | System shall block expensive operations when budget exceeded |
| AC-06 | Historical usage shall be viewable by day/week/month |

**Dashboard Display:**
```
API Usage & Costs
─────────────────────────────────────────
Today:     $0.47  |  ████░░░░░░  (9%)
This Month: $12.30 |  ████████░░  (25%)
Budget:    $50.00
─────────────────────────────────────────
By Model:
  Gemini 3 Flash:  $8.20   (67%)
  GPT-4.5:         $3.10   (25%)
  Claude Opus:     $1.00   (8%)
```

---

#### 5.2.8 [P3] Decision Audit

**Purpose:** Stress-test user investment decisions against thematic alignment.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| DA-01 | User shall submit investment decision for audit |
| DA-02 | Submission shall include: ticker, direction (long/short), thesis |
| DA-03 | System shall evaluate thesis against active themes |
| DA-04 | System shall identify confirmation bias indicators |
| DA-05 | Output shall include alignment score and divergence factors |
| DA-06 | Red flags shall include specific factor explanations |

**Audit Output:**
```
Decision Audit: NVDA Long Position
─────────────────────────────────────────
Your Thesis: "AI infrastructure buildout will drive datacenter GPU demand"

Theme Alignment:
  ✓ AI Infrastructure Buildout     [ALIGNED - 92%]
  ⚠ Semiconductor Capex Slowdown   [PARTIAL - 61%]
  ✗ Tech Valuation Compression     [DIVERGENT - 23%]

Overall Score: 67% ALIGNED

Divergence Factors:
  - Your thesis assumes sustained capex, but 3 sources indicate slowdown
  - Valuation theme suggests multiple compression risk not in your thesis

Recommendation: Review capex sensitivity before proceeding
```

---

#### 5.2.9 [P4] Exposure Recording + Alignment Flags

**Purpose:** Track portfolio exposure and monitor alignment with evolving themes.

**Functional Requirements:**
| ID | Requirement |
|----|-------------|
| ER-01 | User shall manually record portfolio positions |
| ER-02 | Position entry shall include: ticker, direction, size, entry date |
| ER-03 | System shall continuously evaluate positions against themes |
| ER-04 | Aligned positions shall display Green Flag |
| ER-05 | Divergent positions shall display Red Flag with score |
| ER-06 | Divergence score shall explain specific misalignment factors |

**Alignment Logic:**
- Green Flag: Position direction matches theme sentiment for related themes
- Yellow Flag: Mixed signals or theme confidence is LOW
- Red Flag: Position opposes HIGH confidence theme

---

## 6. Technical Architecture

### 6.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              POLARITY ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────────────────────────────────────────────────┐
│   Client    │     │                      Backend                            │
│  (Browser)  │     │                                                         │
├─────────────┤     │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│             │     │  │   Collector │  │   Analyzer  │  │   Chat/Query    │ │
│  Next.js    │◀───▶│  │   Service   │  │   Service   │  │   Service       │ │
│  Frontend   │     │  │  (Cron Job) │  │  (Scheduled)│  │  (On-Demand)    │ │
│             │     │  └──────┬──────┘  └──────┬──────┘  └───────┬─────────┘ │
└─────────────┘     │         │                │                  │          │
                    │         ▼                ▼                  ▼          │
                    │  ┌─────────────────────────────────────────────────┐   │
                    │  │                  Supabase                        │   │
                    │  │  ┌───────────┐ ┌───────────┐ ┌───────────────┐  │   │
                    │  │  │  Articles │ │  Themes   │ │  Chat History │  │   │
                    │  │  │   Table   │ │   Table   │ │     Table     │  │   │
                    │  │  └───────────┘ └───────────┘ └───────────────┘  │   │
                    │  └─────────────────────────────────────────────────┘   │
                    │                                                         │
                    │  ┌─────────────────────────────────────────────────┐   │
                    │  │               External Services                  │   │
                    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │
                    │  │  │ Gemini  │ │  GPT    │ │ Claude  │           │   │
                    │  │  │   API   │ │   API   │ │   API   │           │   │
                    │  │  └─────────┘ └─────────┘ └─────────┘           │   │
                    │  └─────────────────────────────────────────────────┘   │
                    └─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Sources                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │Bloomberg│ │  CNBC   │ │  Yahoo  │ │ Market  │ │ Seeking │  + Paid API  │
│  │   RSS   │ │   RSS   │ │  RSS    │ │  Watch  │ │  Alpha  │  (Optional)  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 14+ (App Router) | SSR, API routes, Vercel deployment |
| **UI Framework** | React + Tailwind CSS | Flexibility for custom terminal UI |
| **State Management** | Zustand or Jotai | Lightweight, sufficient for single-user |
| **Backend Runtime** | Python 3.11+ | Primary language, ML library ecosystem |
| **API Framework** | FastAPI | Async support, type hints, OpenAPI docs |
| **Database** | Supabase (PostgreSQL) | Already configured, real-time capabilities |
| **Vector Store** | pgvector (Supabase) | Embedding storage for clustering |
| **Task Scheduling** | Supabase Edge Functions or External Cron | Serverless scheduled jobs |
| **Hosting** | Vercel (Frontend) + Railway/Fly.io (Backend) | Cost-effective, scalable |
| **AI Models** | Gemini 3 Flash (default), GPT-4.5, Claude Opus | Multi-model support |

### 6.3 Data Model

#### 6.3.1 Core Tables

```sql
-- Articles: All collected news articles
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guid TEXT NOT NULL,
    url TEXT NOT NULL,
    canonical_url TEXT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    full_text TEXT,
    content_mode TEXT NOT NULL DEFAULT 'summary',
    content_hash TEXT,
    source TEXT NOT NULL,
    tier INTEGER NOT NULL DEFAULT 2,
    published_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    info_density_score REAL DEFAULT 0.0,
    word_count INTEGER DEFAULT 0,
    embedding VECTOR(384),  -- For clustering
    is_highlighted BOOLEAN DEFAULT FALSE,

    UNIQUE(guid, source)
);

-- Themes: Identified investment themes
CREATE TABLE themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    sentiment TEXT NOT NULL,
    confidence TEXT NOT NULL,
    confidence_score REAL DEFAULT 0.0,
    industries TEXT[] NOT NULL,
    reasoning TEXT,
    first_detected TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mention_count INTEGER DEFAULT 1,
    trend_status TEXT DEFAULT 'NEW',
    is_active BOOLEAN DEFAULT TRUE
);

-- Theme Citations: Links themes to source articles
CREATE TABLE theme_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID REFERENCES themes(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    quote TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Theme Suggestions: Ticker/ETF mappings
CREATE TABLE theme_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID REFERENCES themes(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    instrument_type TEXT NOT NULL,
    exposure_type TEXT NOT NULL,
    relevance TEXT,
    mentioned_in_sources BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat History: Conversation persistence
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID REFERENCES themes(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    model TEXT,
    citations JSONB,
    token_count INTEGER,
    cost_usd REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Usage: Cost tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model TEXT NOT NULL,
    operation TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Exposures: Portfolio positions (Phase 4)
CREATE TABLE exposures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,  -- 'long' or 'short'
    entry_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.4 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/articles` | GET | List articles with filters |
| `/api/articles/highlights` | GET | Get today's highlighted articles |
| `/api/themes` | GET | List active themes |
| `/api/themes/{id}` | GET | Get theme detail with citations |
| `/api/themes/{id}/suggestions` | GET | Get ticker/ETF suggestions |
| `/api/chat` | POST | Send chat message |
| `/api/chat/deep-analysis` | POST | Trigger multi-model debate |
| `/api/usage` | GET | Get API usage statistics |
| `/api/audit` | POST | Submit decision for audit |
| `/api/exposures` | GET/POST/PUT/DELETE | Manage portfolio exposures |

---

## 7. UI/UX Requirements

### 7.1 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **High Density** | Maximize information per viewport; no excessive whitespace |
| **Terminal Aesthetic** | Monospace fonts, dark theme default, grid-based layouts |
| **Tiled Architecture** | Fixed-width panes that can be resized but not overlapped |
| **No Layout Shift** | Expanding content must not displace other visible elements |
| **Keyboard Navigation** | Power users can navigate entirely via keyboard shortcuts |

### 7.2 Color Palette

```
Background:     #0a0a0a (near black)
Surface:        #1a1a1a (dark gray)
Border:         #333333 (medium gray)
Text Primary:   #e0e0e0 (light gray)
Text Secondary: #888888 (muted gray)
Accent Blue:    #4a9eff (links, highlights)
Bullish Green:  #00c853 (positive sentiment)
Bearish Red:    #ff5252 (negative sentiment)
Neutral Yellow: #ffd740 (neutral/warning)
```

### 7.3 Typography

```
Primary Font:   'JetBrains Mono', 'Fira Code', monospace
Heading Size:   14px (h1), 12px (h2), 11px (h3)
Body Size:      11px
Line Height:    1.4
```

### 7.4 Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  POLARITY                                    [Daily] [Weekly]    12:34 KST  │
├────────────────────┬────────────────────────────────────────────────────────┤
│                    │                                                        │
│   THEME CLUSTERS   │              DETAIL PANE                               │
│   ──────────────   │              ───────────                               │
│                    │                                                        │
│   [List of themes] │   [Theme summary / Article detail / Chat]              │
│                    │                                                        │
│   Fixed width:     │   Flexible width: remaining space                      │
│   300px            │                                                        │
│                    │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│   MY EXPOSURES     │              CONTEXTUAL CHAT                           │
│   ──────────────   │              ────────────────                          │
│                    │                                                        │
│   [Position list]  │   [Chat interface with theme context]                  │
│                    │                                                        │
│   Fixed width:     │   Flexible width: remaining space                      │
│   300px            │                                                        │
│   Fixed height:    │   Fixed height: 250px                                  │
│   200px            │                                                        │
├────────────────────┴────────────────────────────────────────────────────────┤
│  API: $0.47 today | $12.30 MTD | Budget: $50 ████████░░           [?] [⚙]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.5 Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| Desktop (>1200px) | Full tiled layout as designed |
| Tablet (768-1200px) | Stack detail pane below theme list |
| Mobile (<768px) | Single column, tab-based navigation |

Note: Desktop is primary target. Mobile is "functional" not "optimized."

---

## 8. Data Strategy

### 8.1 Source Tiering

| Tier | Sources | Characteristics |
|------|---------|-----------------|
| **Tier 1** | Bloomberg, CNBC | High credibility, market-moving |
| **Tier 2** | Yahoo Finance, MarketWatch, Seeking Alpha, Investing.com | Reputable, broader coverage |
| **Tier 3 (Future)** | Paid APIs (Finnhub, Polygon) | Enhanced coverage if free sources insufficient |

### 8.2 Collection Strategy

**Daily Collection (Automated):**
- Poll RSS feeds every 60 minutes
- Store all unique articles to Supabase
- Compute info-density scores
- Flag top 20% as "highlighted"
- Zero LLM cost

**Weekly Analysis (Scheduled):**
- Query articles from past 7 days
- Generate embeddings (local model)
- Cluster semantically similar articles
- LLM synthesis for each cluster
- Estimated cost: $0.50-1.00 per run

### 8.3 Data Retention

| Data Type | Retention |
|-----------|-----------|
| Articles | 90 days (configurable) |
| Themes | Indefinite (for historical tracking) |
| Chat History | 30 days |
| API Usage | 1 year |

### 8.4 Hybrid Data Approach

**MVP (Free Sources Only):**
- 6 RSS feeds configured
- Expected: 100-300 articles/day
- Sufficient for theme identification

**Enhancement Trigger:**
If after 4 weeks of operation:
- Theme quality is poor (>50% low-confidence themes)
- Coverage gaps identified (missing major market events)

**Then:** Evaluate paid API integration (Finnhub or Polygon, $30-100/mo)

---

## 9. AI/ML Strategy

### 9.1 Model Selection

| Use Case | Model | Rationale |
|----------|-------|-----------|
| **Default Chat** | Gemini 3 Flash | Best cost/performance ratio |
| **Theme Synthesis** | Gemini 3 Flash | Sufficient for summarization |
| **Deep Analysis** | GPT-4.5 + Gemini + Claude | Consensus for complex questions |
| **Embeddings** | all-MiniLM-L6-v2 | Local, fast, free |

### 9.2 Cost Management

**Per-Operation Estimates:**
| Operation | Estimated Cost |
|-----------|----------------|
| Single chat message | $0.005-0.02 |
| Weekly theme analysis | $0.50-1.00 |
| Deep analysis (3 models) | $0.50-1.00 |
| Decision audit | $0.10-0.20 |

**Monthly Budget Scenarios:**
| Usage Level | Estimated Cost |
|-------------|----------------|
| Light (5 chats/day, weekly analysis) | $15-25/mo |
| Moderate (15 chats/day, 2x deep/week) | $30-50/mo |
| Heavy (30 chats/day, daily deep) | $75-100/mo |

### 9.3 Hallucination Mitigation

**Strategy: Flag, Don't Block**

1. **Citation Requirement:** Theme synthesis must include verbatim quotes
2. **Source Linking:** Every claim traced to article or flagged as synthesized
3. **Confidence Signals:** Model outputs include certainty indicators
4. **Multi-Model Validation:** For high-stakes queries, consensus reduces individual model errors

**Flagging System:**
```
[CITED] This claim is directly supported by source article
[SYNTHESIZED] This claim combines information from multiple sources
[MODEL KNOWLEDGE] This claim is from model training, not current articles
```

### 9.4 Prompt Engineering Standards

All prompts must:
- Include explicit citation requirements
- Request structured output (JSON where applicable)
- Specify confidence level requirements
- Prohibit speculation without flagging

---

## 10. Success Metrics

### 10.1 Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Research Time Saved** | 50% reduction | Self-reported weekly time log |
| **Theme Lead Time** | 1-2 weeks ahead of mainstream | Compare theme detection date vs. major media coverage |
| **Decision Quality** | Reduce "regret" trades by 30% | Track trades flagged as divergent that user proceeded with anyway |
| **System Uptime** | 99% | Automated monitoring |
| **Response Latency** | <5s for chat, <2min for analysis | Performance logging |

### 10.2 Qualitative Metrics

| Metric | Assessment Method |
|--------|-------------------|
| **Theme Relevance** | Weekly self-assessment: "Were themes actionable?" |
| **Chat Usefulness** | Per-session rating: "Did this help my understanding?" |
| **UI Efficiency** | Monthly review: "Is the interface helping or hindering?" |

### 10.3 Review Cadence

- **Weekly:** Theme quality review, API cost check
- **Monthly:** Full metrics review, feature prioritization adjustment
- **Quarterly:** Architecture review, data source evaluation

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **RSS feeds become unavailable** | Medium | High | Monitor feed health; maintain backup sources; design for graceful degradation |
| **LLM costs exceed budget** | Medium | Medium | Hard budget caps; usage alerts; tiered model selection |
| **Theme quality is poor** | Medium | High | Tunable clustering parameters; manual quality review; upgrade to paid sources |
| **Hallucination in critical advice** | Low | High | Mandatory citations; synthesis flagging; multi-model validation |
| **Supabase outage** | Low | High | Local SQLite fallback for read operations |
| **Model API changes/deprecation** | Medium | Medium | Abstraction layer for model switching; multi-provider support |

---

## 12. Out of Scope

The following are explicitly **not** included in this PRD:

| Item | Rationale |
|------|-----------|
| Automated trading | User retains manual control |
| Real-time streaming quotes | Not needed for position trader horizon |
| Social media sentiment (Twitter, Reddit) | Adds complexity; can be Phase 5+ |
| Backtesting framework | Separate product concern |
| Multi-user / team features | Single-user personal tool |
| Mobile native app | Web responsive is sufficient |
| Korean language sources | Nice-to-have, not MVP |
| Premium data feeds (Bloomberg Terminal) | Cost prohibitive |

---

## 13. Open Questions

| Question | Owner | Due Date |
|----------|-------|----------|
| Optimal clustering threshold for theme quality? | Engineering | Post-MVP tuning |
| Should weekly analysis run Sunday night or Monday morning? | Stakeholder | Before Phase 1 complete |
| What constitutes "major market event" for coverage gap detection? | Stakeholder | Phase 2 |
| Integration with any existing portfolio tracker? | Stakeholder | Phase 4 |

---

## 14. Appendix

### 14.1 Glossary

| Term | Definition |
|------|------------|
| **Theme** | An investment narrative supported by multiple news sources |
| **Cluster** | A group of semantically similar articles |
| **Info-Density** | A score measuring the factual/numeric content of an article |
| **Cascading** | UI pattern where clicking expands content inline without layout shift |
| **Divergence Score** | Numeric measure of misalignment between position and theme |

### 14.2 Reference Documents

- `theme_analyzer_plan_v3.md` - Technical implementation plan
- Supabase project: `polarity` (ap-northeast-1)

### 14.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-29 | Consultant | Initial draft |

---

**END OF DOCUMENT**
