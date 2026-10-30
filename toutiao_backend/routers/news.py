from fastapi import HTTPException

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_database

from crud import news
router = APIRouter(prefix="/api/news", tags=["news"])

# 接口实现流程
#1.模块化路由 - API接口规范文档
#2.定义模型类 - 数据库表（数据库设计文档）
#3.在crud文件夹之下封装数据库的增删改查方法
#4.在路由处理函数里面调用crud的增删改查方法

@router.get("/categories")
async def get_categories(skip:int = 0, limit:int = 10, db: AsyncSession = Depends(get_database)):
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
        category_id:int = Query(..., alias="categoryId"),
        page:int = 1,
        page_size:int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_database)
):
    #处理分页规则 -> 查询新闻列表 -> 计算总量 -> 计算是否还有更多
    offset = (page - 1) * page_size
    #查询新闻列表
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    #计算总量
    total = await news.get_news_count(db, category_id)
    #计算是否还有更多
    hasMore = total > (offset + page_size)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": hasMore
        }
    }

@router.get("/detail")
async def get_news_detail(news_id:int = Query(..., alias="id"), db: AsyncSession = Depends(get_database)):
    #获取新闻详情 -> 浏览量+1 -> 相关新闻
    #获取新闻详情
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    #更新浏览量
    await news.increase_news_views(db, news_id)
    #相关新闻
    related_news = await news.get_related_news(db, news_id, news_detail.category_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "description": news_detail.description,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "publishTime": news_detail.publish_time,
            "relatedNews": related_news
        }
    }