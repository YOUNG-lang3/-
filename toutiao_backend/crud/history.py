from wsgiref.util import request_uri

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from models.users import User
from models.history import History


async def add_history(news_id: int, user: User, db: AsyncSession):
    new_history = History(news_id=news_id, user_id=user.id)
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)
    return new_history

async def get_history_list(skip: int, page_size: int, user: User, db: AsyncSession):
    query = (select(News, History.view_time)
             .join(History, History.news_id == News.id)
             .where(History.user_id == user.id)
             .offset(skip)
             .limit(page_size))
    res = await db.execute(query)
    histories = res.all()
    return histories

async def get_histories_count(user: User, db: AsyncSession):
    query = select(func.count(History.id)).where(History.user_id == user.id)
    res = await db.execute(query)
    total = res.scalar()
    return total

async def delete_history(history_id: int, user: User, db: AsyncSession):
    query = delete(History).where(History.user_id == user.id, History.id == history_id)
    res = await db.execute(query)
    await db.commit()
    return res.rowcount

async def clear_history(user: User, db: AsyncSession):
    query = delete(History).where(History.user_id == user.id)
    res = await db.execute(query)
    await db.commit()
    return res.rowcount