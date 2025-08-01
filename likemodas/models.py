from typing import Optional, List

import sqlmodel
from. import utils
from.utils.formatting import format_to_cop
from sqlmodel import Field, Relationship, Column, JSON
from sqlalchemy import String, inspect
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
import enum
import math
import pytz

# --- ✅ SOLUCIÓN AL ModuleNotFoundError ---
# Se eliminó la línea `from.about import about_page` que estaba aquí.
# El archivo de modelos (models.py) nunca debe importar componentes de páginas,
# ya que esto crea una importación circular y es incorrecto estructuralmente.
def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    if not utc_dt:
        return "N/A"
    colombia_tz = pytz.timezone("America/Bogota")
    aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    local_dt = aware_utc_dt.astimezone(colombia_tz)
    return local_dt.strftime('%d-%m-%Y %I:%M %p')

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

class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    
    is_verified: bool = Field(default=False, nullable=False)
    user: Optional[LocalUser] = Relationship()
    posts: List = Relationship(back_populates="userinfo")
    verification_tokens: List = Relationship(back_populates="userinfo")
    shipping_addresses: List = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    comments: List["CommentModel"] = Relationship(back_populates="userinfo")
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo")
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)

class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    title: str
    content: str
    price: float = 0.0
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    image_urls: List[str] = sqlmodel.Field(default_factory=list, sa_column=sqlmodel.Column(sqlmodel.JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)
    comments: List["CommentModel"] = Relationship(back_populates="blog_post")
    category: Category = Field(default=Category.OTROS, sa_column=Column(String, server_default=Category.OTROS.value, nullable=False))
    
    @property
    def rating_count(self) -> int:
        return len(self.comments)

    @property
    def average_rating(self) -> float:
        if not self.comments:
            return 0.0
        total_rating = sum(comment.rating for comment in self.comments)
        return total_rating / len(self.comments) if len(self.comments) > 0 else 0.0

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)
    
    @property
    def publish_date_formatted(self) -> str:
        return format_utc_to_local(self.publish_date)
    
    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)
    
    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["created_at_formatted"] = self.created_at_formatted
        d["publish_date_formatted"] = self.publish_date_formatted
        d["price_cop"] = self.price_cop
        d["rating_count"] = self.rating_count
        d["average_rating"] = self.average_rating
        return d

    @property
    def average_rating_display(self) -> str:
        if self.rating_count > 0:
            return f"{self.average_rating:.1f}"
        return ""

class ShippingAddressModel(rx.Model, table=True):
    __tablename__ = "shippingaddress"
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="shipping_addresses")
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    purchase_date: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    shipping_name: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_neighborhood: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")

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
            return
        return [
            f"{item.quantity}x {item.blog_post.title} (a {format_to_cop(item.price_at_purchase)} c/u)"
            for item in self.items
        ]

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["purchase_date_formatted"] = self.purchase_date_formatted
        d["items_formatted"] = self.items_formatted
        d["confirmed_at_formatted"] = self.confirmed_at_formatted
        d["total_price_cop"] = self.total_price_cop
        return d

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    purchase: "PurchaseModel" = Relationship(back_populates="items")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship()
    quantity: int
    price_at_purchase: float

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="notifications")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    
    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)
        
    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["created_at_formatted"] = self.created_at_formatted
        return d

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=utils.timing.get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["created_at_formatted"] = self.created_at_formatted
        return d

class CommentModel(rx.Model, table=True):
    content: str
    rating: int 
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="comments")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship(back_populates="comments")
    votes: List["CommentVoteModel"] = Relationship(back_populates="comment")

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)

    @property
    def likes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.LIKE)
        
    @property
    def dislikes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.DISLIKE)

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["created_at_formatted"] = self.created_at_formatted
        d["likes"] = self.likes
        d["dislikes"] = self.dislikes
        return d

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column(String))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    comment_id: int = Field(foreign_key="commentmodel.id")
    comment: "CommentModel" = Relationship(back_populates="votes")