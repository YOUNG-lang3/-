from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.favorite import Favorite
from models.users import User
from models.news import News

#检查新闻收藏状态
async def get_news_checked(db: AsyncSession, user: User, news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == news_id)
    res = await db.execute(stmt)
    checked_new = res.scalar_one_or_none()
    if not checked_new:
        return False
    return True

#添加收藏
async def add_favorite(db: AsyncSession, user: User, news_id: int):
    new_favorite = Favorite(news_id=news_id, user_id=user.id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    return new_favorite

#删除收藏
async def remove_favorite(db: AsyncSession, user: User, news_id: int):
    query = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == news_id)
    res = await db.execute(query)
    favorite = res.scalar_one_or_none()
    db.delete(favorite)
    await db.commit()

#获取收藏列表
async def get_favorite_list(db: AsyncSession, user: User, skip: int = 0, limit: int = 100):
    stmt =  (select(News, Favorite.created_at)
            .join(Favorite, Favorite.news_id == News.id)
            .where(Favorite.user_id == user.id)
            .offset(skip)
            .limit(limit))
    res = await db.execute(stmt)
    favorite_list = res.all()
    return favorite_list