from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'keepup.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    content = Column(Text)
    source = Column(String, nullable=False, index=True)
    category = Column(String, index=True)  # tech, ai_research, community, news
    published_at = Column(DateTime, nullable=False, index=True)
    scraped_at = Column(DateTime, nullable=False)
    score = Column(Float, default=0.0, index=True)
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    hn_score = Column(Integer, nullable=True)  # HN points or Reddit upvotes
    comment_count = Column(Integer, nullable=True)
    author = Column(String, nullable=True)

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    post_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
