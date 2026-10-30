from sqlalchemy import Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.news import Base


class Favorite(Base):
    __tablename__ = "favorite"

    # 收藏记录只需要创建时间，不需要更新时间
    updated_at = None

    __table_args__ = (
        # 联合唯一约束：同一用户对同一条新闻只能收藏一次（同时自动建立联合索引）
        UniqueConstraint("user_id", "news_id", name="uk_user_news"),
        # 外键反查：按新闻查收藏记录（联合索引最左前缀用不到 news_id，故单独建索引）
        Index("idx_favorite_news", "news_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
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

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
