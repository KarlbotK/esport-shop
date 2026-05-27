from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Result
from app.schemas.__init__ import RecommendRequestDTO, RecommendVO
from app.security.dependencies import get_current_user, get_optional_user
from app.services.recommend_agent import chat_with_recommend_agent

router = APIRouter(prefix="/api/recommend", tags=["Recommend"])


@router.post("/chat")
async def recommend_chat(
    dto: RecommendRequestDTO,
    current_user: dict | None = Depends(get_optional_user),
):
    """Chat with the AI recommendation agent."""
    user_id = current_user["user_id"] if current_user else None
    reply = await chat_with_recommend_agent(dto.message, user_id)
    return Result.success(RecommendVO(reply=reply))
