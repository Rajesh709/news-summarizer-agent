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

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📰 NewsBot AI")
    st.markdown("*Your intelligent news summarizer*")
    st.markdown("---")

    # Health + Scheduler status
    try:
        r = httpx.get(f"{API_URL}/health", timeout=3)
        h = r.json()
        st.markdown(f"{'🟢' if h['status'] == 'healthy' else '🟡'} **API:** {h['status'].title()}")
        st.markdown(f"{'🟢' if h['redis'] else '🔴'} **Redis:** {'Connected' if h['redis'] else 'Disconnected'}")
        st.markdown(f"{'🟢' if h.get('scheduler_running') else '🔴'} **Scheduler:** {'Active' if h.get('scheduler_running') else 'Inactive'}")
        if h.get("next_digest"):
            st.caption(f"⏰ Next digest: {h['next_digest']}")
    except Exception:
        st.markdown("🔴 **API:** Offline")

    st.markdown("---")

    # Daily Email Digest controls
    st.markdown("### 📧 Daily Email Digest")
    st.markdown("Sent automatically at **7:00 AM IST** every day.")
    st.markdown("📬 **To:** rajeshkm.709@gmail.com")

    if st.button("📤 Send Digest Now", use_container_width=True, type="primary"):
        with st.spinner("Sending digest..."):
            try:
                resp = httpx.post(
                    f"{API_URL}/digest/send",
                    json={"recipient": "rajeshkm.709@gmail.com"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    st.success("✅ Digest sent! Check your inbox.")
                else:
                    st.error(f"Failed: {resp.text}")
            except Exception as exc:
                st.error(f"Error: {exc}")

    if st.button("📊 Scheduler Status", use_container_width=True):
        try:
            r = httpx.get(f"{API_URL}/digest/status", timeout=3)
            s = r.json()
            st.json(s)
        except Exception as exc:
            st.error(str(exc))

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
    st.markdown("### 💡 Example Queries")
    examples = [
        "What are today's top headlines?",
        "Latest news about Artificial Intelligence",
        "Show me technology news today",
        "What's trending in the news right now?",
        "Give me news from India",
        "Business headlines today",
        "Sports news today",
        "Health news this week",
        "Latest news about Bitcoin",
        "What's happening with Tesla?",
    ]
    for ex in examples:
        if st.button(f"▶ {ex}", use_container_width=True, key=ex):
            st.session_state._pending = ex
            st.rerun()

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
    st.metric("📧 Auto Digest", "7:00 AM")

st.markdown("---")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
                answer = response.json()["response"] if response.status_code == 200 else f"⚠️ Error: {response.text}"
            except httpx.ConnectError:
                answer = "❌ Cannot connect to the API. Make sure the backend is running on port 8001."
            except httpx.TimeoutException:
                answer = "⏱️ Request timed out. Please try again."
            except Exception as exc:
                answer = f"❌ Error: {exc}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
