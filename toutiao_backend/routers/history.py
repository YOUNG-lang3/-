from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_database
from models.users import User
from schemas.history import HistoryAdd
from utils.auth import get_current_user
from crud import history
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(history_data: HistoryAdd, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    new_history = await history.add_history(history_data.news_id, user, db)
    return success_response(
        message="添加成功",
        data = {
            "userId": new_history.user_id,
            "newsId": new_history.news_id,
            "viewTime": new_history.view_time
        }
    )

@router.get("/list")
async def get_history_list(
        page: int = 1,
        page_size: int = Query(10, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)):
    offset = (page - 1) * page_size
    list = await history.get_history_list(offset, page_size, user, db)
    list_count = await history.get_histories_count(user, db)
    response_data = []
    for news_data, view_time in list:
        response_data.append({
            "id": news_data.id,
            "title": news_data.title,
            "description": news_data.description,
            "image": news_data.image,
            "author": news_data.author,
            "publishTime": news_data.publish_time,
            "categoryId": news_data.category_id,
            "views": news_data.views,
            "viewTime": view_time
        })
    return success_response(data = {
        "list": response_data,
        "total": list_count,
        "hasMore": list_count > offset + page_size
    })

@router.delete("/delete/{history_id}")
async def delete_history(history_id: int = Path(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    await history.delete_history(history_id, user, db)
    return success_response(message="删除成功", data=None)

@router.delete("/clear")
async def clear_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    await history.clear_history(user, db)
    return success_response(message="清空成功")