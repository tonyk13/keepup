from .rss import RSSScraper
from .reddit import RedditScraper
from .hackernews import HNScraper
from .html import HTMLScraper
from .base import BaseScraper
from typing import List

def get_all_scrapers() -> List[BaseScraper]:
    scrapers = []

    # --- AI RESEARCH & LABS (Highest priority) ---
    ai_sources = [
        # Anthropic
        ("anthropic_engineering", "https://www.anthropic.com/engineering", "ai_research", {
            "article_selector": "article, a[href*='/engineering/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("anthropic_research", "https://www.anthropic.com/research", "ai_research", {
            "article_selector": "a[href*='/research/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("anthropic_news", "https://www.anthropic.com/news", "ai_research", {
            "article_selector": "a[href*='/news/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # OpenAI
        ("openai_research", "https://openai.com/research/", "ai_research", {
            "article_selector": "a[href*='/research/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("openai_news", "https://openai.com/news/company-announcements/", "ai_research", {
            "article_selector": "a[href*='/index/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Google AI
        ("google_ai", "https://ai.google/research/", "ai_research", {
            "article_selector": "a[href*='/research/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Meta AI
        ("meta_ai", "https://ai.meta.com/research/", "ai_research", {
            "article_selector": "a[href*='/research/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # DeepSeek
        ("deepseek", "https://api-docs.deepseek.com/news/news260424", "ai_research", {
            "article_selector": "article, div[class*='news']",
            "title_selector": "h1, h2, h3",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Z.ai
        ("zai", "https://docs.z.ai/release-notes/new-released", "ai_research", {
            "article_selector": "article, div[class*='release']",
            "title_selector": "h1, h2, h3",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Qwen
        ("qwen", "https://qwen.ai/research", "ai_research", {
            "article_selector": "a[href*='/research/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # xAI
        ("xai", "https://x.ai/news", "ai_research", {
            "article_selector": "a[href*='/news/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Mistral
        ("mistral", "https://mistral.ai/news", "ai_research", {
            "article_selector": "a[href*='/news/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Cohere
        ("cohere", "https://cohere.com/blog", "ai_research", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Replicate
        ("replicate", "https://replicate.com/blog", "ai_research", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Perplexity
        ("perplexity", "https://www.perplexity.ai/hub", "ai_research", {
            "article_selector": "a",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Stability AI
        ("stability", "https://stability.ai/news", "ai_research", {
            "article_selector": "a[href*='/news/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        # Kimi
        ("kimi", "https://platform.kimi.ai/", "ai_research", {
            "article_selector": "a",
            "title_selector": "span, h2, h3",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
    ]
    for name, url, cat, selectors in ai_sources:
        scrapers.append(HTMLScraper(name, url, cat, selectors))

    # AI tooling & infra (RSS where possible)
    ai_tooling_rss = [
        ("huggingface", "https://huggingface.co/blog/feed.xml", "ai_tooling", "https://huggingface.co/blog"),
        ("langchain", "https://blog.langchain.dev/rss.xml", "ai_tooling", "https://blog.langchain.dev"),
        ("llamaindex", "https://blog.llamaindex.ai/feed", "ai_tooling", "https://blog.llamaindex.ai"),
    ]
    for name, feed_url, cat, site_url in ai_tooling_rss:
        scrapers.append(RSSScraper(name, feed_url, cat, site_url))

    # Pinecone (HTML)
    scrapers.append(HTMLScraper(
        "pinecone", "https://www.pinecone.io/blog/", "ai_tooling",
        { "article_selector": "a[href*='/blog/']", "title_selector": "h2, h3", "link_selector": "a", "date_selector": "time", "summary_selector": "p" }
    ))
    # Weaviate
    scrapers.append(HTMLScraper(
        "weaviate", "https://weaviate.io/blog", "ai_tooling",
        { "article_selector": "a[href*='/blog/']", "title_selector": "h2, h3", "link_selector": "a", "date_selector": "time", "summary_selector": "p" }
    ))

    # --- TECH BLOGS (General engineering — only high-value ones) ---
    tech_blogs = [
        ("netflix", "https://netflixtechblog.medium.com/feed", "tech", "https://netflixtechblog.medium.com/"),
        ("stripe", "https://stripe.com/blog/engineering.rss", "tech", "https://stripe.com/blog/engineering"),
        ("aws_architecture", "https://aws.amazon.com/blogs/architecture/feed/", "tech", "https://aws.amazon.com/blogs/architecture/"),
        ("cloudflare", "https://blog.cloudflare.com/rss/", "tech", "https://blog.cloudflare.com/"),
        ("uber", "https://www.uber.com/us/en/blog/engineering/rss.xml", "tech", "https://www.uber.com/us/en/blog/engineering/"),
        ("datadog", "https://www.datadoghq.com/blog/engineering/feed/", "tech", "https://www.datadoghq.com/blog/engineering/"),
        ("nvidia_dev", "https://developer.nvidia.com/blog/feed/", "tech", "https://developer.nvidia.com/blog"),
        ("google_developers", "https://developers.googleblog.com/feeds/posts/default", "tech", "https://developers.googleblog.com/"),
    ]
    for name, feed_url, category, site_url in tech_blogs:
        scrapers.append(RSSScraper(name, feed_url, category, site_url))

    # Vercel, Supabase, GitHub (RSS)
    dev_platforms = [
        ("vercel", "https://vercel.com/blog/rss.xml", "tech", "https://vercel.com/blog"),
        ("supabase", "https://supabase.com/rss.xml", "tech", "https://supabase.com/blog"),
        ("github_blog", "https://github.blog/feed/", "tech", "https://github.blog"),
    ]
    for name, feed_url, category, site_url in dev_platforms:
        scrapers.append(RSSScraper(name, feed_url, category, site_url))

    # --- ACADEMIC / RESEARCH FEEDS ---
    academic_rss = [
        ("arxiv_cs_ai", "http://export.arxiv.org/rss/cs.AI", "ai_research", "https://arxiv.org/list/cs.AI/recent"),
        ("arxiv_cs_cl", "http://export.arxiv.org/rss/cs.CL", "ai_research", "https://arxiv.org/list/cs.CL/recent"),
        ("bair_berkeley", "https://bair.berkeley.edu/blog/feed.xml", "ai_research", "https://bair.berkeley.edu/blog"),
        ("eleutherai", "https://blog.eleuther.ai/rss.xml", "ai_research", "https://blog.eleuther.ai"),
        ("lilian_weng", "https://lilianweng.github.io/index.xml", "ai_research", "https://lilianweng.github.io"),
        ("stanford_hai", "https://hai.stanford.edu/news?feed=rss", "ai_research", "https://hai.stanford.edu/news"),
    ]
    for name, feed_url, cat, site_url in academic_rss:
        scrapers.append(RSSScraper(name, feed_url, cat, site_url))

    # --- HIGH-SIGNAL INDIVIDUAL AI WRITERS ---
    writer_rss = [
        ("simon_willison", "https://simonwillison.net/atom.xml", "ai_tooling", "https://simonwillison.net"),
        ("chip_huyen", "https://huyenchip.com/feed.xml", "ai_research", "https://huyenchip.com"),
        ("eugene_yan", "https://eugeneyan.com/feed.xml", "ai_research", "https://eugeneyan.com"),
        ("sebastian_raschka", "https://magpieml.substack.com/feed", "ai_research", "https://magpieml.substack.com"),
        ("import_ai", "https://importai.substack.com/feed", "ai_news", "https://importai.substack.com"),
        ("ethan_mollick", "https://oneusefulthing.substack.com/feed", "ai_news", "https://oneusefulthing.substack.com"),
    ]
    for name, feed_url, cat, site_url in writer_rss:
        scrapers.append(RSSScraper(name, feed_url, cat, site_url))

    # --- AI PRODUCT / TOOLING COMPANIES ---
    product_html = [
        ("scale_ai", "https://scale.com/blog", "ai_tooling", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("cursor", "https://cursor.com/blog", "ai_tooling", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("runway", "https://runwayml.com/blog/", "ai_tooling", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("weights_biases", "https://wandb.ai/blog", "ai_tooling", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("ai21", "https://www.ai21.com/blog", "ai_tooling", {
            "article_selector": "a[href*='/blog/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
        ("microsoft_research_ai", "https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/", "ai_research", {
            "article_selector": "a[href*='/research/publication/']",
            "title_selector": "h2, h3, span",
            "link_selector": "a",
            "date_selector": "time",
            "summary_selector": "p",
        }),
    ]
    for name, url, cat, selectors in product_html:
        scrapers.append(HTMLScraper(name, url, cat, selectors))

    # Mastra blog (HTML)
    scrapers.append(HTMLScraper(
        "mastra",
        "https://mastra.ai/blog",
        "ai_tooling",
        {
            "article_selector": "a[href^='/blog/']:not([href*='/page/'])",
            "title_selector": "h2",
            "link_selector": "a",
            "date_selector": "span.block.shrink-0.text-xs",
            "summary_selector": "p.line-clamp-3",
        }
    ))

    # --- AI NEWS / AGGREGATORS ---
    news_sources = [
        ("ai_news", "https://www.artificialintelligence-news.com/feed/", "ai_news", "https://www.artificialintelligence-news.com"),
        ("venturebeat_ai", "https://venturebeat.com/category/ai/feed/", "ai_news", "https://venturebeat.com/category/ai/"),
    ]
    for name, feed_url, cat, site_url in news_sources:
        scrapers.append(RSSScraper(name, feed_url, cat, site_url))

    # --- REDDIT COMMUNITIES ---
    reddits = [
        "ClaudeAI", "ClaudeCode", "LocalLLaMA", "OpenAI",
        "singularity", "codex", "AI_Agents", "opencodeCLI", "LLMDevs",
        "MachineLearning",
    ]
    for sub in reddits:
        scrapers.append(RedditScraper(sub))

    # --- HACKER NEWS (AI-tagged stories where possible) ---
    scrapers.append(HNScraper())

    return scrapers
