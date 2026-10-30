from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

NEWS_APP_URL = "mysql+aiomysql://root:yuyang0613@localhost:3306/news_app?charset=utf8mb4"

#创建异步引擎
async_engine = create_async_engine(
    NEWS_APP_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)
#创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
#创建依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        yield session
