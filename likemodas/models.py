# likemodas/models.py (VERSIÓN ACTUALIZADA)

from typing import Optional, List
from . import utils
from sqlmodel import Field, Relationship, Column, JSON
from sqlalchemy import String
from sqlalchemy import inspect
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
import enum
import math # Importa math para los cálculos

# (Los ENUMs y otros modelos no cambian)
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

# (UserInfo y otros modelos no cambian)
class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    is_verified: bool = Field(default=False, nullable=False)
    user: Optional[LocalUser] = Relationship()
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo")
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

# --- ✨ CAMBIOS AQUÍ ✨ ---
class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    title: str
    content: str
    price: float = 0.0
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)
    comments: List["CommentModel"] = Relationship(back_populates="blog_post")
    
    @property
    def rating_count(self) -> int:
        """Devuelve el número total de comentarios (calificaciones)."""
        return len(self.comments)

    @property
    def average_rating(self) -> float:
        """Calcula la calificación promedio de todos los comentarios."""
        if not self.comments:
            return 0.0
        total_rating = sum(comment.rating for comment in self.comments)
        return total_rating / len(self.comments)

    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")
    
    @property
    def publish_date_formatted(self) -> str:
        if not self.publish_date:
            return ""
        return self.publish_date.strftime("%d-%m-%Y")
    
    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        # Comprueba si los comentarios ya fueron cargados en memoria.
        # Esto evita la "carga perezosa" (lazy load) que causa el error.
        if 'comments' in inspect(self).attrs:
            d["rating_count"] = self.rating_count
            d["average_rating"] = self.average_rating
        else:
            # Si los comentarios no están cargados, devuelve un valor por defecto.
            d["rating_count"] = 0
            d["average_rating"] = 0.0
        return d


# --- FIN DE CAMBIOS ---

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    purchase_date: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")
    @property
    def purchase_date_formatted(self) -> str:
        return self.purchase_date.strftime('%d-%m-%Y %H:%M')
    @property
    def confirmed_at_formatted(self) -> str:
        if not self.confirmed_at:
            return "N/A"
        return self.confirmed_at.strftime('%d-%m-%Y %H:%M')
    @property
    def items_formatted(self) -> list[str]:
        if not self.items:
            return []
        return [f"{item.quantity}x {item.blog_post.title} (@ ${item.price_at_purchase:.2f} c/u)" for item in self.items]
    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["purchase_date_formatted"] = self.purchase_date_formatted
        d["items_formatted"] = self.items_formatted
        d["confirmed_at_formatted"] = self.confirmed_at_formatted
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
        return self.created_at.strftime("%d-%m-%Y %H:%M")
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
        return self.created_at.strftime("%Y-%m-%d %H:%M")
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
        return self.created_at.strftime("%d-%m-%Y %H:%M")
    @property
    def likes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.LIKE)
    @property
    def dislikes(self) -> int:
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.DISLIKE)

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column(String))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    comment_id: int = Field(foreign_key="commentmodel.id")
    comment: "CommentModel" = Relationship(back_populates="votes")