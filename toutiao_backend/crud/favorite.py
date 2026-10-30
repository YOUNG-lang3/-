from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.favorite import Favorite
from models.users import User

#检查新闻收藏状态
async def get_news_checked(db: AsyncSession, user: User, news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == news_id)
    res = await db.execute(stmt)
    checked_new = res.scalar_one_or_none()
    if not checked_new:
        return False
    return True