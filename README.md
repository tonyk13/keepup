# KeepUp

An intelligent content aggregation agent that continuously scrapes top engineering blogs, AI research labs, Reddit communities, and Hacker News — then filters out the noise so you only see high-signal posts.

## Features

- **Continuous Scraping**: Monitors 60+ sources every 60 minutes
- **Noise Filtering**: Built-in heuristic scoring system evaluates every post on technical depth, novelty, and substance
- **Multi-Source Coverage**:
  - **Tech Blogs**: Uber, Netflix, Stripe, AWS Architecture, Cloudflare, Slack, Meta, Datadog, Google Developers, NVIDIA, Dropbox, Discord, LaunchDarkly, Notion
  - **AI Research**: Anthropic, OpenAI, Google AI, Meta AI, DeepSeek, Qwen, Z.ai
  - **Community**: Reddit (r/ClaudeAI, r/LocalLLaMA, r/OpenAI, r/singularity, and more) + Hacker News
- **Smart UI**: Dark-mode dashboard with search, score filtering, source filtering, favorites, and read/unread tracking
- **Auto-Refresh**: Frontend refreshes automatically every 60 seconds

## Architecture

- **Backend**: Python + FastAPI + SQLite + APScheduler
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Scrapers**: Modular RSS, JSON API, and HTML scrapers for each source
- **Evaluator**: Heuristic scoring (0-100) based on technical keywords, novelty signals, content length, code snippets, data presence, and marketing-noise penalties

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

- `GET /api/posts` — list posts (filter by category, source, min_score, search, read, favorite)
- `POST /api/posts/{id}/read` — mark as read
- `POST /api/posts/{id}/favorite` — toggle favorite
- `GET /api/stats` — dashboard stats
- `POST /api/trigger-scrape` — manually trigger a scrape

## Scoring System

Posts are scored 0-100 using a hybrid heuristic:

- **Source reputation**: Research labs and deep-tech blogs get a base boost
- **Technical depth**: Count of technical keywords (distributed systems, LLM, inference, etc.)
- **Novelty**: Announcements, new releases, papers, benchmarks
- **Substance**: Content length, code snippets, numbers/data
- **Marketing penalty**: Hype words and fluff reduce the score
- **Social signals**: HN upvotes / Reddit upvotes add bonus points

## Adding New Sources

Edit `backend/app/scrapers/__init__.py` and add a new scraper instance:

```python
# For RSS feeds
scrapers.append(RSSScraper("my_blog", "https://example.com/feed", "tech", "https://example.com"))

# For HTML scraping
scrapers.append(HTMLScraper("my_blog", "https://example.com", "tech", {
    "article_selector": "article",
    "title_selector": "h2",
    "link_selector": "a",
    "date_selector": "time",
    "summary_selector": "p",
}))
```

## Notes

- HTML scrapers are best-effort and may break if a site redesigns its layout
- Reddit scrapes may be rate-limited; the app handles failures gracefully
- The SQLite database lives at `backend/data/keepup.db`
- All content is deduplicated by URL
