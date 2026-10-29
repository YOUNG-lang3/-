import uuid
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from _datetime import datetime

from models.users import User, UserToken
from schemas.users import UserRequest
from utils.secure import get_hash_password, get_verified_password


#根据用户名查找用户
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

#创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hash_password = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

#生成token
async def create_token(db: AsyncSession, user_id: int):
    #生成token -> 检查是否存在token -> 存在就更新，不存在就创建
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.token == token)
    res = await db.execute(query)
    user_token = res.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
    await db.commit()
    return token

#密码明文校验
async def varify_password(db: AsyncSession, user_id: int, plain_password: str):
    query = select(User.password).where(User.id == user_id)
    res = await db.execute(query)
    hashed_password = res.scalar_one_or_none()
    if not hashed_password:
        raise HTTPException(status_code=404, detail="未找到密码")
    is_valid = get_verified_password(plain_password, hashed_password)
    return is_valid

#根据token查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query_token = select(UserToken).where(UserToken.token == token)
    res_token = await db.execute(query_token)
    db_token = res_token.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query_user = select(User).where(User.id == db_token.user_id)
    res_user = await db.execute(query_user)
    user = res_user.scalar_one_or_none()
    return user