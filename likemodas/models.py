# likemodas/models.py (CORREGIDO Y COMPLETO)

from typing import Optional, List
from . import utils
from sqlmodel import Field, Relationship, Column, JSON
# --- ✨ AÑADIDO: Importar String ---
from sqlalchemy import String
from datetime import datetime, timedelta
import secrets
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class UserInfo(rx.Model, table=True):
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    
    # --- ✨ CORRECCIÓN: Se define explícitamente la columna como String ---
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False)
    )
    is_verified: bool = Field(default=False, nullable=False)
    # --- FIN DE CAMBIOS ---
    
    user: Optional[LocalUser] = Relationship()
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False,
    )

class VerificationToken(rx.Model, table=True):
    """Almacena tokens de un solo uso para la verificación de correo."""
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")

    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )

class PasswordResetToken(rx.Model, table=True):
    """Almacena tokens de un solo uso para el reseteo de contraseña."""
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id") # Se enlaza a LocalUser directamente
    expires_at: datetime

    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    
    purchase_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
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
        return [
            # [cite_start]👇 CORRECCIÓN: Se eliminó el "[cite: 378]"
            f"{item.quantity}x {item.blog_post.title} (@ ${item.price_at_purchase:.2f} c/u)"
            for item in self.items
        ]

    # --- ✨ CORRECCIÓN: AÑADE ESTE MÉTODO ---
    def dict(self, **kwargs):
        """
        Sobrescribe el método dict para incluir las propiedades computadas
        [cite_start]y hacerlas accesibles en el frontend. [cite: 379]
        """
        d = super().dict(**kwargs)
        d["purchase_date_formatted"] = self.purchase_date_formatted
        d["items_formatted"] = self.items_formatted
        # ✨ --- AÑADIR LA NUEVA PROPIEDAD AL DICCIONARIO --- ✨
        d["confirmed_at_formatted"] = self.confirmed_at_formatted
        return d

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    purchase: "PurchaseModel" = Relationship(back_populates="items")
    
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship()
    
    quantity: int
    price_at_purchase: float

class VoteType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

# ... (dentro de la clase UserInfo)
class UserInfo(rx.Model, table=True):
    # ... (campos existentes)
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    # --- 👇 AÑADIR ESTAS DOS LÍNEAS ---
    comments: List["CommentModel"] = Relationship(back_populates="userinfo")
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo")

# ... (dentro de la clase BlogPostModel)
class BlogPostModel(rx.Model, table=True):
    # ... (campos existentes)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # --- 👇 AÑADIR ESTA LÍNEA ---
    comments: List["CommentModel"] = Relationship(back_populates="blog_post")


# --- 👇 AÑADIR ESTOS DOS NUEVOS MODELOS COMPLETOS AL FINAL DEL ARCHIVO ---

class CommentModel(rx.Model, table=True):
    """Almacena un comentario hecho por un usuario en una publicación."""
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relación con el usuario que comentó
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="comments")

    # Relación con la publicación comentada
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship(back_populates="comments")

    # Relación con los votos (likes/dislikes)
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
    """Almacena el voto (like/dislike) de un usuario en un comentario específico."""
    vote_type: VoteType

    # Relación con el usuario que votó
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    
    # Relación con el comentario que fue votado
    comment_id: int = Field(foreign_key="commentmodel.id")
    comment: "CommentModel" = Relationship(back_populates="votes")

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="notifications", sa_relationship_kwargs={"overlaps": "notifications"})

    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    url: Optional[str] = None # URL opcional para redirigir al hacer clic

    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%d-%m-%Y %H:%M")

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["created_at_formatted"] = self.created_at_formatted
        return d

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    title: str
    content: str
    price: float = 0.0
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")
    @property
    def publish_date_formatted(self) -> str:
        if not self.publish_date:
            return ""
        return self.publish_date.strftime("%d-%m-%Y")

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M")
    def dict(self, **kwargs):
        return super().dict(**kwargs) | {"created_at_formatted": self.created_at_formatted}