from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Categories, News
from cache.news_cache import get_cache_categories, set_cache_news_categories

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    #先查缓存
    cached_categories = await get_cache_categories()
    if cached_categories:
        return cached_categories
    #缓存没有命中 → 查数据库
    stmt = select(Categories).offset(skip).limit(limit)
    res = await db.execute(stmt)
    categories = res.scalars().all()
    #查完数据库 → 写入缓存
    await set_cache_news_categories(jsonable_encoder(categories))
    return categories

async def get_news_list(db: AsyncSession, category_id: int = 1,skip: int = 0, limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

async def get_news_count(db: AsyncSession, category_id: int = 1):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    res = await db.execute(stmt)
    return res.scalar_one()

async def get_news_detail(db: AsyncSession, news_id: int = 1):
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def increase_news_views(db: AsyncSession, news_id: int = 1):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    res = await db.execute(stmt)
    await db.commit()

async def get_related_news(db: AsyncSession, news_id: int = 1, category_id: int = 1, limit: int = 5):
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()