# ============================================================================
# likemodas/models/blog.py (CORRECCIÓN APLICADA)
# ============================================================================
from sqlmodel import Field, Relationship, Column, JSON
from typing import Optional
from datetime import datetime
import reflex as rx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .comment import CommentModel
    from .user import UserInfo
from .enums import Category
from .base import format_utc_to_local
from likemodas.utils.formatting import format_to_cop

class BlogPostModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    title: str
    content: str
    price: float = 0.0
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    image_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    category: Category = Field(default=Category.OTROS)

    userinfo: "UserInfo" = Relationship(back_populates="posts")
    comments: list["CommentModel"] = Relationship(back_populates="blog_post")

    @property
    def rating_count(self) -> int:
        return len(self.comments)

    @property
    def average_rating(self) -> float:
        if not self.comments: return 0.0
        return sum(c.rating for c in self.comments) / len(self.comments)

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)

    @property
    def publish_date_formatted(self) -> str:
        return format_utc_to_local(self.publish_date)

    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)