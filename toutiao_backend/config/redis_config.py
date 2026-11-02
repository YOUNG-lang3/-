import json
from typing import Any

import redis.client as redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

#读取缓存(字符串)
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")

#读取缓存(列表或字典)
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"获取JSON缓存失败：{e}")

#设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")