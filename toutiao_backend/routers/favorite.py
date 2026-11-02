from fastapi import Depends, APIRouter, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_database
from crud import favorite
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response
from schemas.favorite import FavoriteAdd

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    is_done = await favorite.get_news_checked(db, user, news_id)
    return success_response(data={"isFavorite": is_done})

@router.post("/add")
async def add_favorite(favorite_data: FavoriteAdd, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    is_favorited = await favorite.get_news_checked(db, user, favorite_data.news_id)
    if is_favorited:
        raise HTTPException(status_code=400, detail="已收藏")
    new_favorite = await favorite.add_favorite(db, user, favorite_data.news_id)
    return success_response(message="收藏成功", data=new_favorite)

@router.delete("/remove")
async def remove_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    is_favorited = await favorite.get_news_checked(db, user, news_id)
    if not is_favorited:
        raise HTTPException(status_code=400, detail="未收藏")
    await favorite.remove_favorite(db, user, news_id)
    return success_response(message="删除成功")

@router.get("/list")
async def get_favorites_list(
        page: int = 1,
        page_size: int = Query(..., alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    offset = (page - 1) * page_size
    favorite_list = await favorite.get_favorite_list(db, user, offset, page_size)
    respond_data = []
    for news_obj, favorite_time in favorite_list:
        respond_data.append({
            "id": news_obj.id,
            "title": news_obj.title,
            "image": news_obj.image,
            "author": news_obj.author,
            "publishTime": news_obj.publish_time,
            "favoriteTime": favorite_time
        })
    return success_response(data=respond_data)