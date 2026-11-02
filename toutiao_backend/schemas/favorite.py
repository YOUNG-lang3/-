from pydantic import BaseModel, Field


class FavoriteAdd(BaseModel):
    news_id: int = Field(alias="newsId")
