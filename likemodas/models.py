# ============================================================================
# likemodas/models.py (SOLUCIÓN FINAL)
# ============================================================================
from __future__ import annotations
from typing import Optional, List
from sqlmodel import Field, Relationship, Column, JSON
import sqlalchemy
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import enum
import pytz
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from .utils.formatting import format_to_cop

# --- Helper Functions ---
def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    if not utc_dt:
        return "N/A"
    colombia_tz = pytz.timezone("America/Bogota")
    if utc_dt.tzinfo is None:
        aware_utc_dt = pytz.utc.localize(utc_dt)
    else:
        aware_utc_dt = utc_dt
    local_dt = aware_utc_dt.astimezone(colombia_tz)
    return local_dt.strftime('%d-%m-%Y %I:%M %p')

# --- Enums ---
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

# --- Models ---
class UserInfo(rx.Model, table=True):
    # ✅ SOLUCIÓN: Se añade mapped_column() para definir explícitamente el tipo de columna.
    email: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("localuser.id"))
    role: Mapped[UserRole] = mapped_column(default=UserRole.CUSTOMER)
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, onupdate=sqlalchemy.func.now(), nullable=False)

    user: Mapped[Optional["LocalUser"]] = Relationship()
    posts: Mapped[List["BlogPostModel"]] = Relationship(back_populates="userinfo")
    verification_tokens: Mapped[List["VerificationToken"]] = Relationship(back_populates="userinfo")
    shipping_addresses: Mapped[List["ShippingAddressModel"]] = Relationship(back_populates="userinfo")
    purchases: Mapped[List["PurchaseModel"]] = Relationship(back_populates="userinfo")
    notifications: Mapped[List["NotificationModel"]] = Relationship(back_populates="userinfo")
    comments: Mapped[List["CommentModel"]] = Relationship(back_populates="userinfo")
    contact_entries: Mapped[List["ContactEntryModel"]] = Relationship(back_populates="userinfo")
    comment_votes: Mapped[List["CommentVoteModel"]] = Relationship(back_populates="userinfo")

class VerificationToken(rx.Model, table=True):
    token: Mapped[str] = mapped_column(unique=True, index=True)
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    expires_at: Mapped[datetime]
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="verification_tokens")

class PasswordResetToken(rx.Model, table=True):
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("localuser.id"))
    expires_at: Mapped[datetime]

class BlogPostModel(rx.Model, table=True):
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(default=0.0)
    attributes: Mapped[dict] = mapped_column(JSON, default={})
    image_urls: Mapped[list[str]] = mapped_column(JSON, default_factory=list)
    publish_active: Mapped[bool] = mapped_column(default=False)
    publish_date: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, onupdate=sqlalchemy.func.now())
    category: Mapped[Category] = mapped_column(default=Category.OTROS)

    userinfo: Mapped["UserInfo"] = Relationship(back_populates="posts")
    comments: Mapped[list["CommentModel"]] = Relationship(back_populates="blog_post")

    @property
    def rating_count(self) -> int: return len(self.comments)
    @property
    def average_rating(self) -> float:
        if not self.comments: return 0.0
        return sum(c.rating for c in self.comments) / len(self.comments)
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)
    @property
    def publish_date_formatted(self) -> str: return format_utc_to_local(self.publish_date)
    @property
    def price_cop(self) -> str: return format_to_cop(self.price)

class ShippingAddressModel(rx.Model, table=True):
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    neighborhood: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    is_default: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="shipping_addresses")

class PurchaseModel(rx.Model, table=True):
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    total_price: Mapped[float] = mapped_column()
    status: Mapped[PurchaseStatus] = mapped_column(default=PurchaseStatus.PENDING)
    purchase_date: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    shipping_name: Mapped[Optional[str]] = mapped_column(default=None)
    shipping_city: Mapped[Optional[str]] = mapped_column(default=None)
    shipping_neighborhood: Mapped[Optional[str]] = mapped_column(default=None)
    shipping_address: Mapped[Optional[str]] = mapped_column(default=None)
    shipping_phone: Mapped[Optional[str]] = mapped_column(default=None)

    items: Mapped[list["PurchaseItemModel"]] = Relationship(back_populates="purchase")
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="purchases")

    @property
    def purchase_date_formatted(self) -> str: return format_utc_to_local(self.purchase_date)
    @property
    def confirmed_at_formatted(self) -> str: return format_utc_to_local(self.confirmed_at)
    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)
    @property
    def items_formatted(self) -> list[str]:
        if not self.items: return []
        return [item.display_name for item in self.items]

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchasemodel.id"))
    blog_post_id: Mapped[int] = mapped_column(ForeignKey("blogpostmodel.id"))
    quantity: Mapped[int] = mapped_column()
    price_at_purchase: Mapped[float] = mapped_column()

    purchase: Mapped["PurchaseModel"] = Relationship(back_populates="items")
    blog_post: Mapped["BlogPostModel"] = Relationship()

    @property
    def display_name(self) -> str:
        title = self.blog_post.title if self.blog_post else "Producto no encontrado"
        return f"{self.quantity} x {title}"

class NotificationModel(rx.Model, table=True):
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    message: Mapped[str] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False)
    url: Mapped[Optional[str]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="notifications")
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("userinfo.id"), default=None)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[Optional[str]] = mapped_column(default=None)
    email: Mapped[Optional[str]] = mapped_column(default=None)
    message: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    userinfo: Mapped[Optional["UserInfo"]] = Relationship(back_populates="contact_entries")
    
    @property
    def created_at_formatted(self) -> str: 
        return format_utc_to_local(self.created_at)

class CommentModel(rx.Model, table=True):
    content: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, onupdate=sqlalchemy.func.now())
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    blog_post_id: Mapped[int] = mapped_column(ForeignKey("blogpostmodel.id"))
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="comments")
    blog_post: Mapped["BlogPostModel"] = Relationship(back_populates="comments")
    votes: Mapped[list["CommentVoteModel"]] = Relationship(back_populates="comment")

class CommentVoteModel(rx.Model, table=True):
    vote_type: Mapped[VoteType] = mapped_column()
    userinfo_id: Mapped[int] = mapped_column(ForeignKey("userinfo.id"))
    comment_id: Mapped[int] = mapped_column(ForeignKey("commentmodel.id"))
    userinfo: Mapped["UserInfo"] = Relationship(back_populates="comment_votes")
    comment: Mapped["CommentModel"] = Relationship(back_populates="votes")

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0
    @property
    def price_cop(self) -> str: return format_to_cop(self.price)
