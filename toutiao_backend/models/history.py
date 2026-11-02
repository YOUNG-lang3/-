from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from models.news import Base


class History(Base):
    __tablename__ = "history"

    # history 表用 view_time 记录浏览时间，没有 created_at、updated_at，排除 Base 中继承的公共字段
    created_at = None
    updated_at = None

    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        Index("idx_view_time", "view_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="新闻ID"
    )
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="浏览时间"
    )

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
