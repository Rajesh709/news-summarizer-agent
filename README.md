# 📰 NewsBot AI — News Summarizer Agent

A production-ready News Summarizer AI Agent that fetches real-time news from 80,000+ sources and summarizes them into **5 clear bullet points** using natural language queries — powered by LangGraph, GPT-4o-mini, and NewsAPI.

🔗 **API Docs:** http://localhost:8001/docs &nbsp;|&nbsp; **Chat UI:** http://localhost:8502

---

## 🧠 What It Can Do

| Query | Response |
|---|---|
| *"What are today's top headlines?"* | Top 5 news stories with sources |
| *"Latest news about AI"* | Searched & summarized in 5 bullets |
| *"Show me technology news"* | Category-filtered top stories |
| *"News from India today"* | Country-specific headlines |
| *"What's trending right now?"* | Top 10 trending topics analysis |
| *"What's happening with Tesla?"* | Company/topic deep search |
| *"Give me sports news"* | Live sports headlines |
| *"Business news this week"* | Weekly business summary |

> 🧠 **Memory** — remembers topics and countries from earlier in the conversation.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Agent** | LangGraph `create_react_agent` (ReAct) |
| **LLM** | OpenAI GPT-4o-mini |
| **News Data** | NewsAPI (80,000+ sources worldwide) |
| **Backend** | FastAPI + Uvicorn (async) |
| **Memory** | Redis (per-session conversation history) |
| **Frontend** | Streamlit chat UI |
| **Deployment** | Docker + Docker Compose |

---

## 📁 Project Structure

```
news-summarizer-agent/
├── app/
│   ├── agent/
│   │   ├── prompts.py          # NewsBot persona & 5-bullet format rules
│   │   └── news_agent.py       # LangGraph agent + singleton
│   ├── api/
│   │   ├── routes.py           # FastAPI endpoints
│   │   └── schemas.py          # Request/response models
│   ├── memory/
│   │   └── redis_memory.py     # Redis session history
│   ├── tools/
│   │   ├── news_client.py      # Async NewsAPI HTTP client
│   │   ├── top_headlines.py    # Today's top headlines tool
│   │   ├── search_news.py      # Keyword/topic search tool
│   │   ├── category_news.py    # Category filter tool
│   │   ├── trending_topics.py  # Trending keyword extractor
│   │   └── country_news.py     # Country-specific news tool
│   ├── utils/
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logger.py           # Structured logging
│   ├── config.py               # Pydantic settings
│   └── main.py                 # FastAPI app
├── tests/
│   └── test_news_tools.py      # Unit tests for all tools
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.streamlit
├── streamlit_app.py            # Chat UI
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## ⚙️ Agent Tools

| Tool | Purpose |
|---|---|
| `get_top_headlines` | Today's top 5 headlines by country |
| `search_news` | Search by keyword/topic (last 1–7 days) |
| `get_category_news` | Filter by: business, tech, sports, health, science, entertainment |
| `get_trending_topics` | Analyze 100 headlines → extract top 10 trending keywords |
| `get_country_news` | Country-specific news (54+ countries supported) |

---

## 🚀 Quick Start

### Step 1 — Get API Keys
- **OpenAI** → https://platform.openai.com/api-keys
- **NewsAPI** (FREE) → https://newsapi.org/register ← *Takes 30 seconds*

### Step 2 — Setup
```bash
git clone https://github.com/Rajesh709/news-summarizer-agent.git
cd news-summarizer-agent
cp .env.example .env
# Edit .env → add OPENAI_API_KEY and NEWS_API_KEY
```

### Step 3 — Start Redis
```bash
# macOS
brew install redis && brew services start redis

# Linux
sudo apt install redis-server && sudo systemctl start redis
```

### Step 4 — Run API
```bash
python3.11 -m uvicorn app.main:app --reload --port 8001
```

### Step 5 — Run UI *(new terminal)*
```bash
python3.11 -m streamlit run streamlit_app.py
```

### Step 6 — Open Browser
- 🖥️ Chat UI → http://localhost:8502
- 📖 API Docs → http://localhost:8001/docs

---

### Docker (One Command)
```bash
cp .env.example .env   # Add your API keys
docker compose up --build
# UI → http://localhost:8502
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/chat` | Chat with the news agent |
| `POST` | `/api/v1/session/clear` | Clear session memory |
| `GET` | `/api/v1/session/{id}/history` | View conversation history |

```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Top tech news today", "session_id": "my-session"}'
```

---

## 📰 Summary Format

Every news response is structured as:

```
📰 Technology News Summary — Jun 19, 2026

• Apple announces new AI chip that doubles performance over previous generation.
• Google DeepMind releases open-source model beating GPT-4 on benchmarks.
• Microsoft invests $3B in Southeast Asia AI infrastructure expansion.
• Meta launches Ray-Ban smart glasses with real-time translation feature.
• OpenAI partners with 10 universities to offer free API access for research.

📌 Key Takeaway: Big Tech is aggressively expanding AI capabilities across
   hardware, models, and global infrastructure in mid-2026.
```

---

## 🌍 Environment Variables

```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
NEWS_API_KEY=your_newsapi_key       # Free at newsapi.org
REDIS_HOST=localhost
REDIS_PORT=6379
APP_PORT=8001
BACKEND_URL=http://localhost:8001
```

---

## 🧪 Tests

```bash
pytest -v
```

---

## 👤 Author

**Rajesh** — [github.com/Rajesh709](https://github.com/Rajesh709)

> Built with ❤️ using LangGraph, FastAPI, NewsAPI, and GPT-4o-mini
