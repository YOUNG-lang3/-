from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud import users

async def get_current_user(authorization: str = Header(..., alias="Authorization"), db: AsyncSession = Depends(get_database)):
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="无效令牌或令牌已过期")
    return  user