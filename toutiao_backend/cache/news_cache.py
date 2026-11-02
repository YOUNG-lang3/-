from typing import List, Dict, Any

from config.redis_config import get_cache, get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"

async def get_cache_categories():
    return await get_json_cache(CATEGORIES_KEY)

async def set_cache_news_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)