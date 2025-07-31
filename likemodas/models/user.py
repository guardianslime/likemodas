from reflex_local_auth import LocalUser
from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
import reflex as rx

# Se usan importaciones condicionales con TYPE_CHECKING
# para evitar que Python intente importar los modelos en un bucle,
# pero permitiendo que el analizador de tipos (y Reflex) los entienda.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .auth import VerificationToken
    from .blog import BlogPostModel
    from .cart import PurchaseModel
    from .comment import CommentModel, CommentVoteModel
    from .contact import ContactEntryModel, NotificationModel
    from .shipping import ShippingAddressModel

from .enums import UserRole

class UserInfo(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["LocalUser"] = Relationship(back_populates="userinfo")
    
    # Las relaciones se definen con strings ("BlogPostModel", etc.)
    # para romper el ciclo de importación durante la ejecución normal de Python.
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo")
    shipping_addresses: List["ShippingAddressModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    comments: List["CommentModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo")
