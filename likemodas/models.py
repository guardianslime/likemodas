# likemodas/models.py (VERSIÓN FINAL CON TYPO CORREGIDO)

from __future__ import annotations
from typing import Optional, List
from datetime import datetime
import enum
import pytz
import reflex as rx
import sqlalchemy
from sqlmodel import Field, Relationship, Column, JSON
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from reflex_local_auth.user import LocalUser
from . import utils
from .utils.formatting import format_to_cop

# --- Funciones de Utilidad ---

def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    """Formatea una fecha UTC a la zona horaria de Colombia."""
    if not utc_dt:
        return "N/A"
    try:
        colombia_tz = pytz.timezone("America/Bogota")
        aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        local_dt = aware_utc_dt.astimezone(colombia_tz)
        return local_dt.strftime('%d-%m-%Y %I:%M %p')
    except Exception:
        return utc_dt.strftime('%Y-%m-%d %H:%M')

# --- Enumeraciones ---

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

class VoteType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Category(str, enum.Enum):
    ROPA = "ropa"
    CALZADO = "calzado"
    MOCHILAS = "mochilas"
    OTROS = "otros"

# --- Modelos de Base de Datos ---

class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id", unique=True)
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    is_verified: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)

    user: Mapped[Optional[LocalUser]] = Relationship()
    posts: Mapped[List[BlogPostModel]] = Relationship(back_populates="userinfo")
    verification_tokens: Mapped[List[VerificationToken]] = Relationship(back_populates="userinfo")
    shipping_addresses: Mapped[List[ShippingAddressModel]] = Relationship(back_populates="userinfo")
    contact_entries: Mapped[List[ContactEntryModel]] = Relationship(back_populates="userinfo")
    purchases: Mapped[List[PurchaseModel]] = Relationship(back_populates="userinfo")
    notifications: Mapped[List[NotificationModel]] = Relationship(back_populates="userinfo")
    comments: Mapped[List[CommentModel]] = Relationship(back_populates="userinfo")
    comment_votes: Mapped[List[CommentVoteModel]] = Relationship(back_populates="userinfo")


class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="verification_tokens")


class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)


class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    title: str
    content: str
    price: float = 0.0
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    category: Category = Field(default=Category.OTROS, nullable=False)
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="posts")
    comments: Mapped[List[CommentModel]] = Relationship(back_populates="blog_post")
    
    @property
    def rating_count(self) -> int:
        return len(self.comments) if self.comments else 0

    @property
    def average_rating(self) -> float:
        if not self.comments:
            return 0.0
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


class ShippingAddressModel(rx.Model, table=True):
    __tablename__ = "shippingaddress"
    userinfo_id: int = Field(foreign_key="userinfo.id")
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    userinfo: Mapped[UserInfo] = Relationship(back_populates="shipping_addresses")


class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    purchase_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    shipping_name: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_neighborhood: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="purchases")
    items: Mapped[List[PurchaseItemModel]] = Relationship(back_populates="purchase")

    @property
    def purchase_date_formatted(self) -> str:
        return format_utc_to_local(self.purchase_date)
        
    @property
    def confirmed_at_formatted(self) -> str:
        return format_utc_to_local(self.confirmed_at)
        
    @property
    def total_price_cop(self) -> str:
        return format_to_cop(self.total_price)

    @property
    def items_formatted(self) -> list[str]:
        if not self.items:
            return []
        return [
            f"{item.quantity}x {item.blog_post.title} (a {format_to_cop(item.price_at_purchase)} c/u)"
            for item in self.items
            if item.blog_post
        ]


class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    quantity: int
    price_at_purchase: float
    
    purchase: Mapped[PurchaseModel] = Relationship(back_populates="items")
    blog_post: Mapped[BlogPostModel] = Relationship()


class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="notifications")
    
    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)


class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)

    userinfo: Mapped[Optional[UserInfo]] = Relationship(back_populates="contact_entries")

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)


class CommentModel(rx.Model, table=True):
    content: str
    rating: int 
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="comments")
    blog_post: Mapped[BlogPostModel] = Relationship(back_populates="comments")
    # --- 👇 LÍNEA CORREGIDA ---
    votes: Mapped[List[CommentVoteModel]] = Relationship(back_populates="comment")

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)

    @property
    def likes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.LIKE)
        
    @property
    def dislikes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.DISLIKE)


class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column(String))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    comment_id: int = Field(foreign_key="commentmodel.id")
    
    userinfo: Mapped[UserInfo] = Relationship(back_populates="comment_votes")
    comment: Mapped[CommentModel] = Relationship(back_populates="votes")