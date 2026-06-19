from datetime import datetime, timedelta
from app.tools.news_client import NewsClient
from app.agent.news_agent import NewsAgent
from app.services.email_service import EmailService
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# AI-focused search queries — fetches from multiple angles
AI_QUERIES = [
    "artificial intelligence",
    "ChatGPT OpenAI",
    "machine learning deep learning",
    "AI robotics automation",
    "generative AI LLM",
]

# ── AI-themed HTML email template ─────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body        {{ font-family:-apple-system,Arial,sans-serif; background:#0d0d1a; margin:0; padding:20px; }}
    .container  {{ max-width:640px; margin:auto; background:#1a1a2e; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(99,102,241,.3); }}

    /* Header */
    .header     {{ background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#06b6d4 100%); padding:36px 28px; text-align:center; }}
    .header h1  {{ color:#fff; margin:0; font-size:28px; letter-spacing:1px; }}
    .header p   {{ color:#e0e7ff; margin:6px 0 0; font-size:14px; }}
    .badge      {{ display:inline-block; background:rgba(255,255,255,.2); color:#fff; border-radius:20px; padding:5px 16px; font-size:12px; font-weight:bold; margin-top:12px; border:1px solid rgba(255,255,255,.3); }}
    .ai-tag     {{ display:inline-block; background:#06b6d4; color:#fff; border-radius:6px; padding:3px 10px; font-size:11px; font-weight:bold; margin-left:8px; }}

    /* Body */
    .body       {{ padding:28px; background:#1a1a2e; }}

    /* 5 Bullets box */
    .summary-box{{ background:#0f0f23; border:1px solid #6366f1; border-radius:10px; padding:20px 22px; margin-bottom:24px; }}
    .summary-box h2 {{ margin:0 0 16px; font-size:15px; color:#a5b4fc; letter-spacing:.5px; }}
    .bullet     {{ display:flex; align-items:flex-start; margin-bottom:14px; }}
    .bullet .num{{ background:linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff; border-radius:50%; width:26px; height:26px; min-width:26px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; margin-top:1px; }}
    .bullet p   {{ margin:0; color:#e2e8f0; font-size:14px; line-height:1.6; }}
    .takeaway   {{ background:linear-gradient(135deg,#1e1b4b,#1e3a5f); border:1px solid #06b6d4; border-radius:8px; padding:14px 16px; margin-top:12px; font-size:13px; color:#67e8f9; }}

    /* Stats row */
    .stats      {{ display:flex; gap:12px; margin-bottom:24px; }}
    .stat-box   {{ flex:1; background:#0f0f23; border:1px solid #374151; border-radius:8px; padding:12px; text-align:center; }}
    .stat-box .num  {{ font-size:20px; font-weight:bold; color:#a5b4fc; }}
    .stat-box .lbl  {{ font-size:11px; color:#6b7280; margin-top:2px; }}

    /* Articles */
    .articles   {{ margin-top:4px; }}
    .articles h2{{ font-size:15px; color:#a5b4fc; border-bottom:1px solid #374151; padding-bottom:10px; margin-bottom:16px; }}
    .article    {{ background:#0f0f23; border:1px solid #374151; border-radius:10px; padding:16px 18px; margin-bottom:12px; }}
    .article:hover {{ border-color:#6366f1; }}
    .article h3 {{ margin:0 0 6px; font-size:14px; color:#f1f5f9; line-height:1.4; }}
    .article .meta  {{ font-size:11px; color:#6b7280; margin-bottom:8px; }}
    .article p  {{ margin:0 0 10px; font-size:13px; color:#94a3b8; line-height:1.5; }}
    .article a  {{ background:#6366f1; color:#fff; text-decoration:none; font-size:11px; font-weight:bold; padding:5px 12px; border-radius:6px; display:inline-block; }}

    /* AI Topics */
    .topics     {{ display:flex; flex-wrap:wrap; gap:8px; margin:20px 0; }}
    .topic-tag  {{ background:#1e1b4b; color:#a5b4fc; border:1px solid #4338ca; border-radius:20px; padding:5px 14px; font-size:12px; font-weight:bold; }}

    /* Footer */
    .footer     {{ background:#0d0d1a; padding:22px 28px; text-align:center; font-size:12px; color:#4b5563; border-top:1px solid #374151; }}
    .footer strong {{ color:#6366f1; }}
  </style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>🤖 AI News Daily</h1>
    <p>Your Personalized AI Intelligence Briefing</p>
    <span class="badge">🌅 Good Morning, Rajesh! — {date}</span>
  </div>

  <!-- Body -->
  <div class="body">

    <!-- Stats -->
    <div class="stats">
      <div class="stat-box">
        <div class="num">{article_count}</div>
        <div class="lbl">AI Articles<br>Analyzed</div>
      </div>
      <div class="stat-box">
        <div class="num">5</div>
        <div class="lbl">Key Points<br>Summarized</div>
      </div>
      <div class="stat-box">
        <div class="num">{source_count}</div>
        <div class="lbl">News<br>Sources</div>
      </div>
      <div class="stat-box">
        <div class="num">GPT-4o</div>
        <div class="lbl">Powered<br>By</div>
      </div>
    </div>

    <!-- 5-Bullet AI Summary -->
    <div class="summary-box">
      <h2>🧠 TODAY'S AI NEWS — 5 KEY POINTS</h2>
      {bullets_html}
      <div class="takeaway">
        ⚡ <strong>Key Takeaway:</strong> {takeaway}
      </div>
    </div>

    <!-- AI Topic Tags -->
    <div class="topics">
      <strong style="font-size:12px;color:#6b7280;width:100%;margin-bottom:4px;">🏷️ Topics covered today:</strong>
      <span class="topic-tag">🤖 Artificial Intelligence</span>
      <span class="topic-tag">💬 ChatGPT / LLMs</span>
      <span class="topic-tag">🧬 Machine Learning</span>
      <span class="topic-tag">🦾 Robotics</span>
      <span class="topic-tag">🎨 Generative AI</span>
    </div>

    <!-- Top AI Articles -->
    <div class="articles">
      <h2>📋 Top AI Stories Today</h2>
      {articles_html}
    </div>

  </div>

  <!-- Footer -->
  <div class="footer">
    <p>🤖 <strong>AI News Daily</strong> — Delivered every morning at {send_time} IST</p>
    <p>Powered by <strong>NewsAPI</strong> · <strong>OpenAI GPT-4o-mini</strong> · <strong>LangGraph</strong></p>
    <p>📧 rajeshkm.709@gmail.com &nbsp;|&nbsp; © 2026 NewsBot AI</p>
  </div>

</div>
</body>
</html>
"""


def _build_bullets_html(bullets: list) -> str:
    html = ""
    for i, bullet in enumerate(bullets, 1):
        html += f"""
        <div class="bullet">
          <div class="num">{i}</div>
          <p>{bullet.strip()}</p>
        </div>"""
    return html


def _build_articles_html(articles: list) -> str:
    html = ""
    for article in articles[:5]:
        title  = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown")
        desc   = article.get("description") or ""
        url    = article.get("url", "#")
        pub    = article.get("publishedAt", "")
        if pub:
            try:
                dt  = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                pub = dt.strftime("%b %d, %Y · %I:%M %p UTC")
            except Exception:
                pass
        html += f"""
        <div class="article">
          <h3>{title}</h3>
          <div class="meta">📰 {source} &nbsp;|&nbsp; 🕐 {pub}</div>
          <p>{desc[:180]}{'...' if len(desc) > 180 else ''}</p>
          <a href="{url}" target="_blank">Read full story →</a>
        </div>"""
    return html


async def _fetch_ai_articles(client: NewsClient) -> list:
    """Fetch AI news from multiple search queries and deduplicate by URL."""
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    seen_urls = set()
    all_articles = []

    for query in AI_QUERIES:
        try:
            data = await client.get("/everything", {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 5,
            })
            for article in data.get("articles", []):
                url = article.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append(article)
        except Exception as exc:
            logger.warning("ai_fetch_query_failed", query=query, error=str(exc))

    # Sort by published date (newest first)
    all_articles.sort(key=lambda a: a.get("publishedAt", ""), reverse=True)
    return all_articles[:10]


async def build_and_send_digest(recipient: str) -> dict:
    """
    Fetches today's AI news, summarizes via GPT into 5 bullets,
    and sends a beautiful HTML email to the recipient.
    """
    logger.info("ai_digest_starting", recipient=recipient)

    # 1. Fetch AI articles
    client = NewsClient()
    try:
        articles = await _fetch_ai_articles(client)
        if not articles:
            logger.warning("ai_digest_no_articles")
            return {"success": False, "reason": "No AI articles found"}
    finally:
        await client.close()

    # Count unique sources
    sources = {a.get("source", {}).get("name", "") for a in articles}

    # 2. Build article text for GPT context
    article_text = "\n\n".join([
        f"Title: {a.get('title', '')}\n"
        f"Source: {a.get('source', {}).get('name', '')}\n"
        f"Summary: {a.get('description') or ''}"
        for a in articles[:8]
    ])

    # 3. Ask GPT to summarize into 5 AI-focused bullets
    agent = NewsAgent()
    digest_prompt = (
        f"Here are today's top AI news articles:\n\n{article_text}\n\n"
        "Summarize these into EXACTLY 5 bullet points focused on AI developments. "
        "Each bullet should highlight one key AI news insight. "
        "Format:\n"
        "BULLET1: <sentence>\n"
        "BULLET2: <sentence>\n"
        "BULLET3: <sentence>\n"
        "BULLET4: <sentence>\n"
        "BULLET5: <sentence>\n"
        "TAKEAWAY: <one sentence about today's overall AI trend>\n"
        "Be concise, specific, and factual. No fluff."
    )
    ai_response = await agent.chat("ai-digest-session", digest_prompt)
    await agent.close()

    # 4. Parse bullets and takeaway
    bullets = []
    takeaway = "AI continues to evolve rapidly with new breakthroughs across multiple domains."

    for line in ai_response.split("\n"):
        line = line.strip()
        for prefix in ["BULLET1:", "BULLET2:", "BULLET3:", "BULLET4:", "BULLET5:"]:
            if line.startswith(prefix):
                text = line.replace(prefix, "").strip()
                if text:
                    bullets.append(text)
                break
        if line.startswith("TAKEAWAY:"):
            takeaway = line.replace("TAKEAWAY:", "").strip()

    # Fallback parser
    if len(bullets) < 3:
        bullets = [
            l.strip().lstrip("•-*123456789. ")
            for l in ai_response.split("\n")
            if len(l.strip()) > 30 and not l.lower().startswith("takeaway")
        ][:5]

    bullets = bullets[:5]

    # 5. Build HTML email
    now = datetime.now()
    html = HTML_TEMPLATE.format(
        date=now.strftime("%A, %B %d, %Y"),
        send_time=now.strftime("%I:%M %p"),
        article_count=len(articles),
        source_count=len(sources),
        bullets_html=_build_bullets_html(bullets),
        takeaway=takeaway,
        articles_html=_build_articles_html(articles),
    )

    # 6. Send email
    email_svc = EmailService()
    subject = f"🤖 Your Daily AI News Digest — {now.strftime('%b %d, %Y')}"
    success = email_svc.send(to=recipient, subject=subject, html_body=html)

    result = {
        "success": success,
        "recipient": recipient,
        "articles_fetched": len(articles),
        "sources": len(sources),
        "bullets_generated": len(bullets),
        "sent_at": now.isoformat(),
        "topic": "Artificial Intelligence",
    }
    logger.info("ai_digest_complete", **result)
    return result
