from reflex_local_auth import LocalUser
from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
import sqlalchemy
import reflex as rx

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .auth import VerificationToken

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .blog import BlogPostModel

from likemodas.models.cart import PurchaseModel

if TYPE_CHECKING:
    from .comment import CommentModel, CommentVoteModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .contact import ContactEntryModel, NotificationModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .shipping import ShippingAddressModel

from .enums import UserRole

class UserInfo(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_verified: bool = Field(default=False)

    user: Optional["LocalUser"] = Relationship(back_populates="userinfo")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones hacia otros modelos (usando comillas para evitar ciclos)
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo")
    shipping_addresses: List["ShippingAddressModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    comments: List["CommentModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo")
