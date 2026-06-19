from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.api.schemas import (
    ChatRequest, ChatResponse, HealthResponse,
    ClearSessionRequest, DigestRequest, DigestResponse,
)
from app.agent.news_agent import get_agent, NewsAgent
from app.memory.redis_memory import RedisMemoryManager
from app.scheduler import get_scheduler_status
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_memory_manager = None


def _get_memory_manager() -> RedisMemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = RedisMemoryManager()
    return _memory_manager


# ── Health ────────────────────────────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse)
async def health_check():
    redis_ok = await _get_memory_manager().ping()
    scheduler = get_scheduler_status()
    return HealthResponse(
        status="healthy" if redis_ok else "degraded",
        redis=redis_ok,
        scheduler_running=scheduler.get("running", False),
        next_digest=scheduler.get("next_run"),
    )


# ── Chat ──────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, agent: NewsAgent = Depends(get_agent)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    response = await agent.chat(request.session_id, request.message)
    return ChatResponse(response=response, session_id=request.session_id)


# ── Manual Digest Trigger ─────────────────────────────────────────────────────
@router.post("/digest/send", response_model=DigestResponse)
async def send_digest_now(request: DigestRequest, background_tasks: BackgroundTasks):
    """Manually trigger the news digest email immediately."""
    from app.services.daily_digest import build_and_send_digest
    from app.config import get_settings

    recipient = request.recipient or get_settings().digest_recipient
    logger.info("manual_digest_triggered", recipient=recipient)

    # Run in background so the API responds immediately
    background_tasks.add_task(build_and_send_digest, recipient)

    return DigestResponse(
        message=f"📧 Digest is being sent to {recipient}. Check your inbox in ~30 seconds.",
        recipient=recipient,
    )


# ── Scheduler Status ──────────────────────────────────────────────────────────
@router.get("/digest/status")
async def digest_status():
    """Get current scheduler status and next scheduled run time."""
    from app.config import get_settings
    settings = get_settings()
    status = get_scheduler_status()
    return {
        **status,
        "digest_time": settings.digest_time,
        "timezone": settings.digest_timezone,
        "recipient": settings.digest_recipient,
    }


# ── Session ───────────────────────────────────────────────────────────────────
@router.post("/session/clear")
async def clear_session(request: ClearSessionRequest):
    await _get_memory_manager().clear_session(request.session_id)
    return {"message": f"Session '{request.session_id}' cleared."}


@router.get("/session/{session_id}/history")
async def get_history(session_id: str):
    from app.memory.redis_memory import get_session_history
    history = get_session_history(session_id)
    messages = history.messages
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": [{"role": m.type, "content": m.content} for m in messages],
    }
