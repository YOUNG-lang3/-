from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.users import varify_password, create_token
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdate, UserUpdatePassword
from crud import users
from starlette import status

from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_database)):
    #查询用户
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    #创建用户
    new_user = await users.create_user(db, user_data)
    #生成token
    token = await users.create_token(db, new_user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": new_user.id,
    #             "username": new_user.username,
    #             "bio": new_user.bio,
    #             "avatar": new_user.avatar
    #         }
    #     }
    # }
    # 封装返回内容
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(new_user))
    return success_response(message="注册成功", data=response_data)

@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_database)):
    #检查用户是否存在
    existing_user = await users.get_user_by_username(db, user_data.username)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")
    #校验密码
    is_valid = await varify_password(db, existing_user.id, user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码错误")
    #生成token
    token = await create_token(db, existing_user.id)
    #封装返回内容
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(existing_user))
    return success_response(message="登录成功", data=response_data)

@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    response_data = UserInfoResponse.model_validate(user)
    return success_response(message="获取用户信息成功", data=response_data)

@router.put("/update")
async def update_user_info(update_info: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    res = await users.update_user_info(db, update_info, user.username)
    response_data = UserInfoResponse.model_validate(res)
    return success_response(message="更改用户信息成功", data=response_data)

# @router.put("/password")
# async def update_user_password(user_data: UserUpdatePassword, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
#     res = await users.update_user_password(db, user_data, user.username)
#     response_data = UserInfoResponse.model_validate(res)
#     return success_response(message="修改密码成功", data=response_data)
@router.put("/password")
async def update_user_password(password_data: UserUpdatePassword, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    await users.update_user_password(db, user, password_data)
    return success_response(message="密码修改成功")