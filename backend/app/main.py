import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

def strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', clean).strip()

from .db import init_db, get_db, SessionLocal, Post, Source
from .evaluator import evaluate_post, is_junk_post
from .scrapers import get_all_scrapers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Initialize DB on startup
init_db()

# Seed sources — upsert any new ones
def seed_sources(db: Session):
    existing_names = {s.name for s in db.query(Source).all()}
    scrapers = get_all_scrapers()
    for sc in scrapers:
        if sc.name not in existing_names:
            db.add(Source(name=sc.name, url=sc.url, category=sc.category))
    db.commit()

# Background scraping job
def run_scrapers_sync():
    db = SessionLocal()
    try:
        asyncio.run(_run_scrapers(db))
    finally:
        db.close()

async def _run_scrapers(db: Session):
    scrapers = get_all_scrapers()
    for scraper in scrapers:
        try:
            posts = await scraper.scrape()
            source_name = scraper.name
            added = 0
            for p in posts:
                if not p.get("url"):
                    continue
                existing = db.query(Post).filter(Post.url == p["url"]).first()
                if existing:
                    continue
                title = p.get("title", "")
                content = p.get("content", "")
                # Hard junk filter: skip nav links and empty spam
                if is_junk_post(title, content, source_name):
                    continue
                score = evaluate_post(
                    title,
                    content,
                    source_name,
                    category=scraper.category,
                    published_at=p.get("published_at"),
                    hn_score=p.get("hn_score"),
                    comment_count=p.get("comment_count"),
                )
                # Minimum quality gate: don't store obviously bad posts
                if score < 12:
                    continue
                # If scraper couldn't find a date, use sentinel instead of lying with "now"
                published_at = p.get("published_at")
                if not published_at:
                    published_at = datetime(1970, 1, 1)

                post = Post(
                    title=p["title"],
                    url=p["url"],
                    content=p.get("content", "")[:3000],
                    source=source_name,
                    category=scraper.category,
                    published_at=published_at,
                    scraped_at=datetime.utcnow(),
                    score=score,
                    author=p.get("author"),
                    hn_score=p.get("hn_score"),
                    comment_count=p.get("comment_count"),
                )
                db.add(post)
                added += 1
            db.commit()
            # Update source metadata
            src = db.query(Source).filter(Source.name == source_name).first()
            if src:
                src.last_scraped_at = datetime.utcnow()
                src.post_count += added
                db.commit()
            print(f"[{datetime.now().isoformat()}] {source_name}: {added} new posts")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ERROR scraping {scraper.name}: {e}")
            try:
                db.rollback()
            except Exception:
                pass

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_sources(db)
    finally:
        db.close()
    # Schedule recurring scrape every 60 minutes
    scheduler.add_job(
        lambda: asyncio.create_task(_run_scrapers(SessionLocal())),
        IntervalTrigger(minutes=60),
        id="scrape_all",
        replace_existing=True,
    )
    scheduler.start()
    # Initial scrape in background after a short delay so startup completes
    async def delayed_initial():
        await asyncio.sleep(3)
        db2 = SessionLocal()
        try:
            await _run_scrapers(db2)
        finally:
            db2.close()
    asyncio.create_task(delayed_initial())
    yield
    scheduler.shutdown()

app = FastAPI(title="KeepUp", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/posts")
def list_posts(
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    exclude_source: Optional[str] = Query(None),
    min_score: float = Query(0.0),
    since: Optional[str] = Query(None),  # 1d, 7d, 30d, 90d, 180d, 365d
    search: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    is_favorite: Optional[bool] = Query(None),
    sort: str = Query("score"),  # score, date
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if category:
        query = query.filter(Post.category == category)
    if source:
        query = query.filter(Post.source == source)
    if exclude_source:
        excluded = [s.strip() for s in exclude_source.split(",") if s.strip()]
        if excluded:
            query = query.filter(~Post.source.in_(excluded))
    if min_score is not None:
        query = query.filter(Post.score >= min_score)
    if since:
        try:
            days = int(since[:-1])
            unit = since[-1]
            if unit == 'd':
                cutoff = datetime.utcnow() - timedelta(days=days)
                query = query.filter(Post.published_at >= cutoff)
        except (ValueError, IndexError):
            pass
    if search:
        like = f"%{search}%"
        query = query.filter(Post.title.ilike(like) | Post.content.ilike(like))
    if is_read is not None:
        query = query.filter(Post.is_read == is_read)
    if is_favorite is not None:
        query = query.filter(Post.is_favorite == is_favorite)

    if sort == "date":
        query = query.order_by(Post.published_at.desc())
    elif sort == "score":
        query = query.order_by(Post.score.desc(), Post.published_at.desc())
    else:
        query = query.order_by(Post.published_at.desc())

    total = query.count()
    posts = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "url": p.url,
                "content": strip_html(p.content),
                "source": p.source,
                "category": p.category,
                "published_at": p.published_at.isoformat() if p.published_at else None,
                "score": p.score,
                "is_read": p.is_read,
                "is_favorite": p.is_favorite,
                "hn_score": p.hn_score,
                "comment_count": p.comment_count,
                "author": p.author,
            }
            for p in posts
        ],
    }

@app.post("/api/posts/{post_id}/read")
def mark_read(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_read = True
    db.commit()
    return {"ok": True}

@app.post("/api/posts/{post_id}/unread")
def mark_unread(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_read = False
    db.commit()
    return {"ok": True}

@app.post("/api/posts/{post_id}/favorite")
def toggle_favorite(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_favorite = not post.is_favorite
    db.commit()
    return {"ok": True, "is_favorite": post.is_favorite}

@app.get("/api/sources")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.is_active == True).all()
    return [
        {
            "name": s.name,
            "url": s.url,
            "category": s.category,
            "last_scraped_at": s.last_scraped_at.isoformat() if s.last_scraped_at else None,
            "post_count": s.post_count,
        }
        for s in sources
    ]

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Post).count()
    unread = db.query(Post).filter(Post.is_read == False).count()
    favorites = db.query(Post).filter(Post.is_favorite == True).count()
    today = datetime.utcnow().date()
    today_count = db.query(Post).filter(Post.scraped_at >= today).count()
    avg_score = db.query(Post).filter(Post.score > 0).with_entities(Post.score).all()
    avg = sum(s[0] for s in avg_score) / len(avg_score) if avg_score else 0
    return {
        "total_posts": total,
        "unread_posts": unread,
        "favorite_posts": favorites,
        "posts_today": today_count,
        "average_score": round(avg, 2),
    }

@app.post("/api/trigger-scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    db = SessionLocal()
    background_tasks.add_task(_run_scrapers, db)
    return {"ok": True, "message": "Scrape triggered in background"}

@app.post("/api/re-evaluate")
def re_evaluate_all(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    updated = 0
    for p in posts:
        new_score = evaluate_post(
            p.title,
            p.content,
            p.source,
            category=p.category,
            published_at=p.published_at,
            hn_score=p.hn_score,
            comment_count=p.comment_count,
        )
        if abs(new_score - p.score) > 0.1:
            p.score = new_score
            updated += 1
    db.commit()
    return {"ok": True, "updated": updated}

# Serve frontend in production (optional, for local dev we run separately)
from fastapi.staticfiles import StaticFiles
import os
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
