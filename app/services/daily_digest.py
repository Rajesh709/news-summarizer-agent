from datetime import datetime
from app.tools.news_client import NewsClient
from app.tools.top_headlines import _format_articles
from app.agent.news_agent import NewsAgent
from app.services.email_service import EmailService
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── HTML email template ───────────────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body        {{ font-family: -apple-system, Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px; }}
    .container  {{ max-width:640px; margin:auto; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,.1); }}
    .header     {{ background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%); padding:32px 28px; text-align:center; }}
    .header h1  {{ color:#fff; margin:0; font-size:26px; }}
    .header p   {{ color:#a0c4ff; margin:6px 0 0; font-size:14px; }}
    .badge      {{ display:inline-block; background:#e94560; color:#fff; border-radius:20px; padding:4px 14px; font-size:12px; font-weight:bold; margin-top:10px; }}
    .body       {{ padding:28px; }}
    .summary-box{{ background:#f0f7ff; border-left:4px solid #0f3460; border-radius:6px; padding:18px 20px; margin-bottom:24px; }}
    .summary-box h2{{ margin:0 0 14px; font-size:16px; color:#0f3460; }}
    .bullet     {{ display:flex; align-items:flex-start; margin-bottom:12px; }}
    .bullet .num{{ background:#0f3460; color:#fff; border-radius:50%; width:24px; height:24px; min-width:24px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; margin-top:1px; }}
    .bullet p   {{ margin:0; color:#333; font-size:14px; line-height:1.5; }}
    .takeaway   {{ background:#fff3cd; border:1px solid #ffc107; border-radius:6px; padding:14px 16px; margin-top:8px; font-size:13px; color:#856404; }}
    .articles   {{ margin-top:24px; }}
    .articles h2{{ font-size:16px; color:#333; border-bottom:2px solid #eee; padding-bottom:8px; margin-bottom:16px; }}
    .article    {{ border:1px solid #eee; border-radius:8px; padding:14px 16px; margin-bottom:12px; }}
    .article h3 {{ margin:0 0 6px; font-size:14px; color:#1a1a2e; }}
    .article .meta{{ font-size:12px; color:#888; margin-bottom:6px; }}
    .article p  {{ margin:0; font-size:13px; color:#555; line-height:1.4; }}
    .article a  {{ color:#0f3460; text-decoration:none; font-size:12px; font-weight:bold; }}
    .categories {{ display:flex; flex-wrap:wrap; gap:8px; margin:20px 0; }}
    .cat-btn    {{ background:#eef2ff; color:#0f3460; border-radius:20px; padding:6px 14px; font-size:12px; font-weight:bold; text-decoration:none; }}
    .footer     {{ background:#f8f9fa; padding:20px 28px; text-align:center; font-size:12px; color:#888; border-top:1px solid #eee; }}
    .footer a   {{ color:#0f3460; }}
  </style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>📰 NewsBot AI</h1>
    <p>Your Daily Morning Briefing — {date}</p>
    <span class="badge">🌅 Good Morning, Rajesh!</span>
  </div>

  <!-- Body -->
  <div class="body">

    <!-- 5-Bullet Summary -->
    <div class="summary-box">
      <h2>🗞️ Today's Top News — 5 Key Points</h2>
      {bullets_html}
      <div class="takeaway">
        📌 <strong>Key Takeaway:</strong> {takeaway}
      </div>
    </div>

    <!-- Category Quick Links -->
    <div class="categories">
      <strong style="font-size:13px;color:#333;width:100%;margin-bottom:4px;">Browse by Category:</strong>
      <span class="cat-btn">💼 Business</span>
      <span class="cat-btn">💻 Technology</span>
      <span class="cat-btn">⚽ Sports</span>
      <span class="cat-btn">🏥 Health</span>
      <span class="cat-btn">🎬 Entertainment</span>
      <span class="cat-btn">🔬 Science</span>
    </div>

    <!-- Top Articles -->
    <div class="articles">
      <h2>📋 Top Stories</h2>
      {articles_html}
    </div>

  </div>

  <!-- Footer -->
  <div class="footer">
    <p>Delivered by <strong>NewsBot AI</strong> every morning at {send_time} IST</p>
    <p>Powered by NewsAPI · OpenAI GPT-4o-mini · LangGraph</p>
    <p>© 2026 NewsBot AI · rajeshkm.709@gmail.com</p>
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
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown")
        desc = article.get("description") or ""
        url = article.get("url", "#")
        published = article.get("publishedAt", "")
        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published = dt.strftime("%b %d, %Y · %I:%M %p UTC")
            except Exception:
                pass
        html += f"""
        <div class="article">
          <h3>{title}</h3>
          <div class="meta">📰 {source} &nbsp;|&nbsp; 🕐 {published}</div>
          <p>{desc[:180]}{'...' if len(desc) > 180 else ''}</p>
          <a href="{url}" target="_blank">Read full story →</a>
        </div>"""
    return html


async def build_and_send_digest(recipient: str) -> dict:
    """
    Fetches today's top headlines, summarizes via GPT into 5 bullets,
    and sends a beautiful HTML email to the recipient.
    Returns a status dict.
    """
    settings = get_settings()
    logger.info("daily_digest_starting", recipient=recipient)

    # 1. Fetch raw articles from NewsAPI
    client = NewsClient()
    try:
        data = await client.get("/top-headlines", {
            "country": "us",
            "pageSize": 10,
            "category": "general",
        })
        articles = data.get("articles", [])
        if not articles:
            logger.warning("daily_digest_no_articles")
            return {"success": False, "reason": "No articles found"}
    finally:
        await client.close()

    # 2. Use the AI Agent to generate 5-bullet summary + takeaway
    agent = NewsAgent()
    digest_prompt = (
        "Fetch and summarize today's top news into EXACTLY 5 bullet points. "
        "Format your response as:\n"
        "BULLET1: <sentence>\n"
        "BULLET2: <sentence>\n"
        "BULLET3: <sentence>\n"
        "BULLET4: <sentence>\n"
        "BULLET5: <sentence>\n"
        "TAKEAWAY: <one sentence key takeaway>\n"
        "Be concise and factual."
    )
    ai_response = await agent.chat("daily-digest-session", digest_prompt)
    await agent.close()

    # 3. Parse bullets and takeaway from AI response
    bullets = []
    takeaway = "Today's news reflects a diverse range of global events."
    for line in ai_response.split("\n"):
        line = line.strip()
        for prefix in ["BULLET1:", "BULLET2:", "BULLET3:", "BULLET4:", "BULLET5:",
                       "• ", "- ", "* "]:
            if line.startswith(prefix):
                text = line.replace(prefix, "").strip().lstrip("•-* ")
                if text:
                    bullets.append(text)
                break
        if line.startswith("TAKEAWAY:"):
            takeaway = line.replace("TAKEAWAY:", "").strip()

    # Fallback: split by newlines if parsing failed
    if len(bullets) < 3:
        bullets = [
            l.strip().lstrip("•-*123456789. ")
            for l in ai_response.split("\n")
            if len(l.strip()) > 30 and not l.strip().startswith("TAKEAWAY")
        ][:5]

    bullets = bullets[:5]

    # 4. Build HTML email
    now = datetime.now()
    html = HTML_TEMPLATE.format(
        date=now.strftime("%A, %B %d, %Y"),
        send_time=now.strftime("%I:%M %p"),
        bullets_html=_build_bullets_html(bullets),
        takeaway=takeaway,
        articles_html=_build_articles_html(articles),
    )

    # 5. Send email
    email_svc = EmailService()
    subject = f"📰 Your Morning News Digest — {now.strftime('%b %d, %Y')}"
    success = email_svc.send(to=recipient, subject=subject, html_body=html)

    result = {
        "success": success,
        "recipient": recipient,
        "articles_fetched": len(articles),
        "bullets_generated": len(bullets),
        "sent_at": now.isoformat(),
    }
    logger.info("daily_digest_complete", **result)
    return result
