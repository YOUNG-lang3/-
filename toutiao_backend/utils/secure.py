from passlib.context import CryptContext

#创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)

#密码校验
def get_verified_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password, hash_password)