
from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_database
from crud.favorite import get_news_checked
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    is_done = await get_news_checked(db, user, news_id)
    return success_response(data={"isFavorite", is_done})