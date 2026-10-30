import uuid
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession
from _datetime import datetime

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdate, UserUpdatePassword
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

#更新用户信息：更新信息 → 检查是否命中 → 获取更新后的用户返回
async def update_user_info(db: AsyncSession, user_info: UserUpdate, username: str):
    query = update(User).where(User.username == username).values(**user_info.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    res = await db.execute(query)
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="修改失败")
    updated_user = await get_user_by_username(db, username)
    return updated_user

# #修改用户密码
# async def update_user_password(db: AsyncSession, user_data: UserUpdatePassword, username: str):
#     query = select(User.password).where(User.username == username)
#     res = await db.execute(query)
#     hashed_password = res.scalar_one_or_none()
#     if not hashed_password:
#         raise HTTPException(status_code=404, detail="用户未登录")
#     is_right = get_verified_password(user_data.old_password, hashed_password)
#     if not is_right:
#         raise HTTPException(status_code=404, detail="旧密码错误")
#     query_password = update(User).where(User.username == username).values(password = get_hash_password(user_data.new_password))
#     await db.execute(query_password)
#     await db.commit()
#     user = await get_user_by_username(db, username)
#     return user

#修改用户密码（新版）
async def update_user_password(db: AsyncSession, user: User, password_data: UserUpdatePassword):
    if not get_verified_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    hashed_new_password = get_hash_password(password_data.new_password)
    user.password = hashed_new_password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True