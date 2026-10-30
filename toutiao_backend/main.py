from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import news, users, favorite
from utils.exception import register_exception_handlers
app = FastAPI()

# 注册全局异常处理器
register_exception_handlers(app)

@app.get('/')
async def root():
    return {"hello world"}

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)

#解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)