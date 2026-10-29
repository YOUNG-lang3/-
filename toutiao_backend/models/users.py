from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.news import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（加密存储）")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    gender: Mapped[str] = mapped_column(
        Enum("male", "female", "unknown"),
        default="unknown",
        comment="性别"
    )
    bio: Mapped[Optional[str]] = mapped_column(String(500), comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname})>"


class UserToken(Base):
    __tablename__ = "user_token"

    # user_token 表只有 created_at，没有 updated_at，排除 Base 中继承的该公共字段
    updated_at = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
