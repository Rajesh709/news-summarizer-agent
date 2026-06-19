import uuid
import httpx
import streamlit as st
import os

st.set_page_config(
    page_title="NewsBot AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api/v1"

# ── Session state ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📰 NewsBot AI")
    st.markdown("*Your intelligent news summarizer*")
    st.markdown("---")

    st.markdown("**Session**")
    st.code(st.session_state.session_id[:8] + "...", language=None)

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        with httpx.Client() as c:
            try:
                c.post(f"{API_URL}/session/clear", json={"session_id": st.session_state.session_id})
            except Exception:
                pass
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Try These Queries")

    categories = {
        "🌍 Top Headlines": [
            "What are today's top news headlines?",
            "Give me top news from India",
            "What's happening in the UK today?",
        ],
        "🔍 Search News": [
            "Latest news about Artificial Intelligence",
            "What's the news about Tesla today?",
            "Bitcoin latest news",
            "News about India elections",
        ],
        "📂 By Category": [
            "Show me today's technology news",
            "What's the latest sports news?",
            "Business headlines today",
            "Health news this week",
        ],
        "🔥 Trending": [
            "What's trending in the news right now?",
            "What are people talking about today?",
        ],
    }

    for section, examples in categories.items():
        st.markdown(f"**{section}**")
        for example in examples:
            if st.button(f"▶ {example}", use_container_width=True, key=example):
                st.session_state._pending = example
                st.rerun()

    st.markdown("---")
    # Health badge
    try:
        r = httpx.get(f"{API_URL}/health", timeout=3)
        h = r.json()
        st.markdown(f"{'🟢' if h['status'] == 'healthy' else '🟡'} **API**: {h['status'].title()}")
        st.markdown(f"{'🟢' if h['redis'] else '🔴'} **Redis**: {'Connected' if h['redis'] else 'Disconnected'}")
    except Exception:
        st.markdown("🔴 **API**: Offline")

# ── Main chat area ────────────────────────────────────────────────────────────
st.title("📰 NewsBot AI — News Summarizer Agent")
st.markdown("Ask me anything about today's news. I'll fetch real articles and summarize them in **5 key points**.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌍 Countries", "54+")
with col2:
    st.metric("📂 Categories", "7")
with col3:
    st.metric("🔍 Search Depth", "7 days")
with col4:
    st.metric("📰 Sources", "80,000+")

st.markdown("---")

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle button clicks
pending = st.session_state.pop("_pending", None)
user_input = st.chat_input("Ask about any news topic, country, or category...") or pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("📡 Fetching and summarizing news..."):
            try:
                response = httpx.post(
                    f"{API_URL}/chat",
                    json={"message": user_input, "session_id": st.session_state.session_id},
                    timeout=60.0,
                )
                if response.status_code == 200:
                    answer = response.json()["response"]
                else:
                    answer = f"⚠️ Backend error ({response.status_code}): {response.text}"
            except httpx.ConnectError:
                answer = "❌ Cannot connect to the API. Make sure the backend is running on port 8001."
            except httpx.TimeoutException:
                answer = "⏱️ Request timed out. Please try again."
            except Exception as exc:
                answer = f"❌ Error: {exc}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
