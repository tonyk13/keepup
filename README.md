# KeepUp

An intelligent AI news aggregator website that continuously scrapes top AI research labs, tech blogs, arXiv, newsletters, Reddit, and Hacker News - then scores and filters out the noise so you only see high-signal posts.

## Features

- **Continuous Scraping**: Monitors 60+ sources every 60 minutes
- **AI-First Scoring**: Heuristic scoring (0–100) with strong bias toward AI/ML substance; filters marketing fluff and generic noise
- **Smart Defaults**: Loads with past week + min score 75 + arXiv hidden - so you see fresh, high-signal news immediately
- **Multi-Source Coverage**:
  - **AI Research Labs**: Anthropic, OpenAI, Google AI, Meta AI, xAI, Mistral, Cohere, DeepSeek, Qwen, Stability AI
  - **AI Tooling**: Hugging Face, LangChain, LlamaIndex, Pinecone, Weaviate, Cursor, Replicate, Mastra
  - **Academic**: arXiv CS.AI, arXiv CS.CL, BAIR Berkeley, EleutherAI
  - **Writers & Newsletters**: Lilian Weng, Import AI, Ethan Mollick, Chip Huyen, Sebastian Raschka, Eugene Yan
  - **Tech Blogs**: Netflix, Stripe, AWS, Cloudflare, Datadog, NVIDIA, Vercel, GitHub, Google Developers
  - **Community**: Reddit (r/ClaudeAI, r/LocalLLaMA, r/OpenAI, r/MachineLearning, and more) + Hacker News
- **arXiv Toggle**: Research papers hidden by default; click to show when you want deep dives
- **Date Filter**: View posts from past week, month, 3 months, 6 months, or year
- **Light & Dark Mode**: Defaults to light mode; toggleable
- **Mobile-First UI**: Fully responsive dashboard built with Tailwind CSS
- **Auto-Refresh**: Frontend refreshes automatically every 60 seconds

## Architecture

- **Backend**: Python + FastAPI + SQLite + APScheduler
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Scrapers**: Modular RSS, JSON API, and HTML scrapers for each source
- **Evaluator**: Heuristic scoring based on AI keywords, novelty signals, content length, code snippets, data presence, recency boost, and marketing-noise penalties

## Design Decisions

**Why SQLite?**
I chose SQLite because the project is intentionally self-contained - no external DB server to provision or manage. For ~3K posts and a single-user read-heavy workload, SQLite with WAL mode is more than sufficient. If I ever need concurrent writers or horizontal scaling, migrating to Postgres is straightforward.

**Why heuristic scoring instead of an LLM?**
LLM inference would make every scrape expensive, slow, and non-deterministic. A tuned heuristic gives instant, reproducible scores on every run. I iterated on keyword weights and penalties until the top results consistently matched what I'd actually want to read.

**Why modular scrapers?**
Each source gets its own scraper class (RSS, HTML, API). This isolates failures - if Anthropic changes their markup, only that scraper breaks. It also makes adding new sources a one-line change.

**Why FastAPI?**
Async-native out of the box, automatic OpenAPI docs, and native support for background tasks (used for on-demand scrapes). The API surface is small but fully typed.

**Why hide arXiv by default?**
Research papers are high-signal but they absolutely dominate the top scores because every abstract is dense with AI terminology. Hiding them by default keeps the feed balanced with news, product launches, and commentary. The toggle lets you dive into papers when you want them.

**Why sentinel dates?**
When a scraper can't parse a date, the honest thing to do is admit it rather than stamp "today" on everything. We use `1970-01-01` as a sentinel and display "Unknown date" in the UI. The recency boost in the scorer skips sentinel dates so they don't unfairly rank higher.

## Quick Start

### 1. Install dependencies

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
npm run build
```

### 2. Run

```bash
./start.sh
```

Then open http://localhost:8000 in your browser.

Or manually:

```bash
# Terminal 1
cd backend
source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 (for dev with hot reload)
cd frontend
npm run dev
```

### 3. API

- `GET /api/posts` - list posts (filter by category, source, min_score, since, search, read, favorite, exclude_source)
- `POST /api/posts/{id}/read` - mark as read
- `POST /api/posts/{id}/favorite` - toggle favorite
- `GET /api/stats` - dashboard stats
- `POST /api/trigger-scrape` - manually trigger a scrape
- `POST /api/re-evaluate` - re-score all existing posts

## Scoring System

Posts are scored 0-100 using a hybrid heuristic:

- **Source reputation**: AI research labs and high-signal writers get a base boost
- **AI Core Keywords**: LLM, transformer, RLHF, agent, inference, benchmark, etc. (highest weight)
- **Novelty**: Announcements, new releases, papers, open-source models
- **Substance**: Content length, code snippets, numbers/data
- **Recency**: Fresh posts get a small score bump
- **Marketing penalty**: Hype words and fluff reduce the score
- **Social signals**: HN upvotes / Reddit upvotes add bonus points
- **Junk filter**: Generic nav-link titles and empty posts are blocked before storage

## Adding New Sources

Edit `backend/app/scrapers/__init__.py` and add a new scraper instance:

```python
# For RSS feeds
scrapers.append(RSSScraper("my_blog", "https://example.com/feed", "ai_news", "https://example.com"))

# For HTML scraping
scrapers.append(HTMLScraper("my_blog", "https://example.com", "ai_news", {
    "article_selector": "article",
    "title_selector": "h2",
    "link_selector": "a",
    "date_selector": "time",
    "summary_selector": "p",
}))
```

## Deployment

The included `render.yaml` + `build.sh` are configured for Render:

1. Push to GitHub
2. Create a new Blueprint on Render and select this repo
3. Deploy

## Notes

- HTML scrapers are best-effort and may break if a site redesigns its layout
- Reddit scrapes may be rate-limited; the app handles failures gracefully
- The SQLite database lives at `backend/data/keepup.db`
- All content is deduplicated by URL
- Posts without parseable dates show "Unknown date" instead of faking today's date
