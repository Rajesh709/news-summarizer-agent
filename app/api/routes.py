from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse, ClearSessionRequest
from app.agent.news_agent import get_agent, NewsAgent
from app.memory.redis_memory import RedisMemoryManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_memory_manager = None


def _get_memory_manager() -> RedisMemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = RedisMemoryManager()
    return _memory_manager


@router.get("/health", response_model=HealthResponse)
async def health_check():
    redis_ok = await _get_memory_manager().ping()
    return HealthResponse(status="healthy" if redis_ok else "degraded", redis=redis_ok)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, agent: NewsAgent = Depends(get_agent)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    response = await agent.chat(request.session_id, request.message)
    return ChatResponse(response=response, session_id=request.session_id)


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
