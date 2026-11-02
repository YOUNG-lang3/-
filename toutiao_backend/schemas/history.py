from pydantic import BaseModel, Field


class HistoryAdd(BaseModel):
    news_id: int = Field(alias="newsId")