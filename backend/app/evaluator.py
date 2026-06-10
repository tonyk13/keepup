import re
from typing import Dict, Any

# AI-Centric Content Evaluation
# Scores posts 0-100 with strong bias toward AI/ML substance and signal

# Tier 1: Core AI/ML terminology — highest value
AI_CORE_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "transformer", "attention mechanism", "diffusion model", "generative ai",
    "large language model", "llm", "foundation model", "multimodal model",
    "reinforcement learning", "rlhf", "human feedback", "alignment",
    "fine-tuning", "pre-training", "pretraining", "instruction tuning",
    "inference", "training run", "compute cluster", "gpu cluster",
    "mixture of experts", "moe", "sparse model", "dense model",
    "quantization", "distillation", "pruning", "model compression",
    "rag", "retrieval augmented generation", "vector database", "embedding",
    "prompt engineering", "chain of thought", "tool use", "function calling",
    "agent", "ai agent", "autonomous agent", "multi-agent",
    "synthetic data", "data augmentation", "curriculum learning",
    "hallucination", "jailbreak", "adversarial", "safety",
    "interpretability", "mechanistic interpretability", "feature visualization",
    "scaling law", "compute optimal", "chinchilla", "emergent abilities",
    "benchmark", "evaluation", " leaderboard", "mmlu", "hellaswag",
    "gpqa", "human eval", "pass@k", "bleu", "rouge", "perplexity",
    "open source model", "open weight", "weights released", "model checkpoint",
    "arxiv", "paper", "research", "study", "ablation",
    "context window", "long context", "infinite context", "sliding window",
    "token", "vocabulary", "tokenizer", "bpe", "sentencepiece",
    "cuda", "tpu", "triton", "kernel fusion", "flash attention",
    "stable diffusion", "midjourney", "dall-e", "sora", "video generation",
    "speech recognition", "tts", "text to speech", "asr",
    "coding assistant", "copilot", "code generation", "code completion",
    "gpt", "claude", "gemini", "llama", "mistral", "qwen", "deepseek",
    "o1", "o3", "reasoning model", "test-time compute",
]

# Tier 2: AI-adjacent / infra / product
AI_ADJACENT_KEYWORDS = [
    "ai-powered", "ai driven", "mlops", "model serving", "inference server",
    "batch inference", "online inference", "edge inference",
    "observability", "monitoring", "tracing", "evals",
    "feature store", "data pipeline", "etl", "data lake",
    "kubernetes", "docker", "container", "microservices",
    "api", "sdk", "grpc", "rest api", "websocket",
    "latency", "throughput", "qps", "tps", "rps",
    "scalability", "sharding", "replication", "load balancing",
    "cloud", "aws", "gcp", "azure", "serverless", "lambda",
    "database", "vector store", "pinecone", "weaviate", "chroma",
    "redis", "postgres", "nosql", "mongodb",
    "frontend", "react", "nextjs", "vercel", "deployment",
    "security", "privacy", "encryption", "pii", "gdpr",
]

# Signals of high-value AI news
NOVELTY_KEYWORDS = [
    "announcing", "introducing", "launch", "released", "release",
    "new model", "new paper", "new research", "new benchmark",
    "state-of-the-art", "sota", "breakthrough", "improvement",
    "update", "version", "v1.", "v2.", "v3.", "open source",
    "open weight", "open model", "available now", "public",
    "chatgpt", "claude", "gemini", "grok", "pi", "character",
]

# Marketing fluff that dilutes signal
MARKETING_NOISE = [
    "revolutionary", "game-changer", "game changer", "synergy", "leverage",
    "unlock potential", "empower", "journey", "story", "inspiring",
    "innovative", "disruptive", "thought leader", "impactful",
    "passionate", "excited to announce", "thrilled", "delighted",
    "proud to", "celebrate", "milestone", "culture", "diversity",
    "inclusion", "belonging", "wellness", "mindfulness",
    "customer success", "digital transformation", "future of work",
    "unlocking value", "driving innovation", "paradigm shift",
    "game changing", "cutting edge", "next generation", "world class",
]

# Non-AI topics that should reduce score from general tech blogs
NON_AI_TOPICS = [
    "fintech", "crypto", "bitcoin", "blockchain", "web3", "nft",
    "real estate", "automotive", "airline", "retail", "ecommerce",
    "marketing", "sales", "crm", "hr", "recruiting",
    "supply chain", "logistics", "manufacturing", "agriculture",
    "healthcare it", "electronic health record", "telemedicine",
    "food delivery", "ride sharing", "gig economy",
    "esg", "sustainability", "climate", "carbon neutral",
    "diversity equity inclusion", "dei", "employee engagement",
]

def _count_keywords(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)

def _estimate_content_length(content: str) -> int:
    if not content:
        return 0
    return len(content.split())

def _has_code_snippets(text: str) -> bool:
    if not text:
        return False
    code_indicators = [
        "def ", "class ", "function ", "const ", "let ", "var ",
        "import ", "from ", "require(", "```", "<code", "<pre",
        "{", "}", ";", "# ", "// ", "/*",
    ]
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in code_indicators)

def _has_numbers_or_data(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r"\d+\.?\d*%", r"\d+\s*ms", r"\d+\s*gb", r"\d+\s*tb",
        r"\d+\.?\d*x", r"\d+\.?\d*\s*fps", r"\d+\.?\d*\s*tps",
        r"arxiv", r"et al", r"\d+\.?\d*\s*accuracy",
        r"\d+\.?\d*\s*parameters", r"\d+\.?\d*\s*billion",
        r"mmlu", r"hellaswag", r"gpqa", r"humaneval",
        r"pass@", r"bleu-\d+", r"rouge-\d+",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

from datetime import datetime, timedelta

def evaluate_post(title: str, content: str, source: str, category: str = "", published_at: datetime = None, hn_score: int = None, comment_count: int = None) -> float:
    full_text = f"{title} {content or ''}"
    score = 40.0  # Lower neutral base to let AI signals shine

    # 1. Source reputation & category weighting
    # AI research labs get massive base boosts
    source_category_weights = {
        "anthropic_research": 22, "anthropic_engineering": 20, "anthropic_news": 18,
        "openai_research": 22, "openai_news": 18,
        "google_ai": 18, "meta_ai": 18,
        "deepseek": 18, "xai": 18, "mistral": 16, "cohere": 14,
        "qwen": 16, "zai": 14, "stability": 14, "replicate": 12,
        "perplexity": 12, "kimi": 14,
        "huggingface": 15, "langchain": 12, "llamaindex": 12,
        "pinecone": 10, "weaviate": 10,
        "ai_news": 8, "venturebeat_ai": 8,
        "nvidia_dev": 10,
        # Academic / Research (moderate weight so fresh news/blogs can compete)
        "arxiv_cs_ai": 10, "arxiv_cs_cl": 10,
        "bair_berkeley": 14, "eleutherai": 14,
        "lilian_weng": 16, "stanford_hai": 12,
        # Writers
        "simon_willison": 14, "chip_huyen": 16,
        "eugene_yan": 16, "sebastian_raschka": 14,
        "import_ai": 14, "ethan_mollick": 14,
        # Product / Tooling
        "scale_ai": 12, "cursor": 14, "runway": 12,
        "weights_biases": 12, "ai21": 12,
        "mastra": 14,
        "microsoft_research_ai": 14,
        "hackernews": 0,
        "reddit": 0,
    }
    for key, weight in source_category_weights.items():
        if key in source.lower():
            score += weight
            break

    # Category-level base boost
    category_boost = {
        "ai_research": 10,
        "ai_tooling": 6,
        "ai_news": 4,
        "tech": 0,
        "community": 0,
    }
    score += category_boost.get(category, 0)

    # 2. AI Core depth (most important signal)
    ai_core_count = _count_keywords(full_text, AI_CORE_KEYWORDS)
    # Slightly lower multiplier so extremely dense sources (e.g. arXiv) don't auto-max
    score += min(ai_core_count * 3, 24)

    # 3. AI Adjacent depth
    ai_adj_count = _count_keywords(full_text, AI_ADJACENT_KEYWORDS)
    score += min(ai_adj_count * 1.5, 10)

    # 4. Novelty / newsworthiness
    novelty_count = _count_keywords(full_text, NOVELTY_KEYWORDS)
    score += min(novelty_count * 3, 12)

    # 5. Substance signals
    content_len = _estimate_content_length(content)
    if content_len > 400:
        score += 3
    if content_len > 1000:
        score += 4
    if _has_code_snippets(full_text):
        score += 4
    if _has_numbers_or_data(full_text):
        score += 5

    # 6. Non-AI topic penalty (for general tech blogs)
    non_ai_count = _count_keywords(full_text, NON_AI_TOPICS)
    if non_ai_count >= 2:
        score -= 15
    elif non_ai_count == 1:
        score -= 5

    # 7. Marketing noise penalty
    noise_count = _count_keywords(full_text, MARKETING_NOISE)
    score -= min(noise_count * 5, 20)

    # 8. Social signals
    if hn_score:
        if hn_score > 200:
            score += 10
        elif hn_score > 100:
            score += 7
        elif hn_score > 50:
            score += 4
        elif hn_score > 20:
            score += 2
    if comment_count:
        if comment_count > 100:
            score += 6
        elif comment_count > 50:
            score += 4
        elif comment_count > 20:
            score += 2

    # 9. Title quality heuristics
    if title:
        clickbait_patterns = [
            r"^\d+ (things|ways|tips|reasons) to",
            r"you won't believe", r"shocking", r"amazing",
            r"how i ", r"what happened when", r"this is why",
        ]
        if any(re.search(p, title, re.IGNORECASE) for p in clickbait_patterns):
            score -= 12

        # Strong AI signals in title get extra boost
        if any(kw in title.lower() for kw in ["announcing", "launch", "released", "new model", "new paper", "open source"]):
            score += 4
        if any(kw in title.lower() for kw in ["gpt", "claude", "llama", "mistral", "gemini", "deepseek", "o1", "o3"]):
            score += 3
        # "Paper" bonus is smaller for arXiv since every entry is a paper
        if "paper" in title.lower() or "research" in title.lower():
            if "arxiv" in source.lower():
                score += 1
            else:
                score += 3

    # 10. Recency boost — fresh news/happenings get a small edge
    # Skip sentinel dates (1970-01-01) used when scraper couldn't find a real date
    if published_at and published_at.year > 2000:
        age = datetime.utcnow() - published_at
        if age < timedelta(hours=24):
            score += 6
        elif age < timedelta(hours=72):
            score += 3
        elif age < timedelta(days=7):
            score += 1

    # 11. Massive penalty for generic navigation-link titles that slip through HTML scrapers
    generic_titles = {
        "untitled", "research", "blog", "news", "home", "about",
        "contact", "archive", "page", "posts", "articles", "resources",
        "documentation", "docs", "api", "products", "solutions",
        "company", "careers", "jobs", "privacy", "terms", "license",
        "read the latest article", "latest article", "latest post",
        "read more", "learn more", "click here", "view all",
    }
    title_lower = (title or "").strip().lower()
    if title_lower in generic_titles or len(title_lower) < 3:
        score -= 50
    # Empty content + generic title is almost certainly nav spam
    if not content and title_lower in generic_titles:
        score -= 30

    # Clamp 0-100
    return max(0.0, min(100.0, score))


# Hard gate: posts that should never enter the database
def is_junk_post(title: str, content: str, source: str) -> bool:
    title_lower = (title or "").strip().lower()
    content_lower = (content or "").strip().lower()

    # Block obviously generic nav-link titles
    generic_titles = {
        "untitled", "research", "blog", "news", "home", "about",
        "contact", "archive", "page", "posts", "articles", "resources",
        "documentation", "docs", "api", "products", "solutions",
        "company", "careers", "jobs", "privacy", "terms", "license",
        "platform", "sign in", "sign up", "login", "logout", "account",
        "read the latest article", "latest article", "latest post",
        "read more", "learn more", "click here", "view all",
    }
    if title_lower in generic_titles:
        return True

    # Block empty or near-empty titles
    if len(title_lower) < 3:
        return True

    # Block posts with zero content AND short/generic titles (nav link spam)
    if not content_lower and len(title_lower) < 20:
        return True

    # Block posts where title is literally just the source domain name
    domain_parts = source.lower().replace("_", "").replace("-", "")
    if title_lower.replace(" ", "").replace("-", "") in domain_parts:
        return True

    return False
