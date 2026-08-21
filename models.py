from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]]
    
    items: Mapped[List["TrackedItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class TrackedItem(Base):
    __tablename__ = 'tracked_items'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    url: Mapped[str]
    title: Mapped[Optional[str]]
    current_price: Mapped[Optional[float]]
    target_price: Mapped[float]
    
    check_interval: Mapped[int] = mapped_column(default=60)
    last_checked: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    
    user: Mapped["User"] = relationship(back_populates="items")