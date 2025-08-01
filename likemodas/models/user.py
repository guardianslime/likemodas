# ============================================================================
# likemodas/models/user.py (CORREGIDO)
# ============================================================================
from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .token import VerificationToken
    from .blog import BlogPostModel
    from .cart import PurchaseModel
    from .comment import CommentModel, CommentVoteModel
    from .contact import ContactEntryModel, NotificationModel
    from .shipping import ShippingAddressModel

from .enums import UserRole

class LocalUser(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: bytes
    userinfo: Optional["UserInfo"] = Relationship(back_populates="user")

class UserInfo(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["LocalUser"] = Relationship(back_populates="userinfo")
    posts: list["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: list["VerificationToken"] = Relationship(back_populates="userinfo")
    shipping_addresses: list["ShippingAddressModel"] = Relationship(back_populates="userinfo")
    purchases: list["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: list["NotificationModel"] = Relationship(back_populates="userinfo")
    comments: list["CommentModel"] = Relationship(back_populates="userinfo")
    contact_entries: list["ContactEntryModel"] = Relationship(back_populates="userinfo")
    comment_votes: list["CommentVoteModel"] = Relationship(back_populates="userinfo")
