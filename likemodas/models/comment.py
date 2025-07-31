from sqlmodel import Field, Relationship, Column
from typing import List
from datetime import datetime
import reflex as rx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .blog import BlogPostModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserInfo
from .base import format_utc_to_local
from .enums import VoteType

class CommentModel(rx.Model, table=True):
    content: str
    rating: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")

    userinfo: "UserInfo" = Relationship(back_populates="comments")
    blog_post: "BlogPostModel" = Relationship(back_populates="comments")
    votes: List["CommentVoteModel"] = Relationship(back_populates="comment")

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column("vote_type", nullable=False))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    comment_id: int = Field(foreign_key="commentmodel.id")

    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    comment: "CommentModel" = Relationship(back_populates="votes")
