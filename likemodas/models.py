# likemodas/models.py

from typing import Optional, List
from datetime import datetime
import enum
import pytz
import reflex as rx
import sqlalchemy
from sqlmodel import Field, Relationship, Column, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String
from reflex_local_auth.user import LocalUser
from .utils.timing import get_utc_now
from .utils.formatting import format_to_cop

# --- Adelanta la declaración de modelos ---
if "CommentModel" not in locals():
    CommentModel = "CommentModel"
if "PurchaseItemModel" not in locals():
    PurchaseItemModel = "PurchaseItemModel"

# --- ✨ INICIO: AÑADIR/REEMPLAZAR ESTE MODELO COMPLETO ✨ ---
class LocalAuthSession(rx.Model, table=True):
    """
    Un modelo local que replica la tabla de sesión de reflex-local-auth
    para resolver problemas de importación y definición.
    """
    __tablename__ = "localauthsession"
    
    user_id: int = Field(nullable=False)
    session_id: str = Field(max_length=255, unique=True, index=True, nullable=False)
    expiration: datetime = Field(
        sa_type=sqlalchemy.DateTime(timezone=True),
        nullable=False,
        sa_column_kwargs={"server_default": sqlalchemy.func.now()}
    )

    # Esta línea evita el error "Table is already defined"
    __table_args__ = {"extend_existing": True}
# --- ✨ FIN: AÑADIR/REEMPLAZAR ESTE MODELO COMPLETO ✨ ---


# --- Funciones de Utilidad ---
def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    if not utc_dt:
        return "N/A"
    try:
        colombia_tz = pytz.timezone("America/Bogota")
        aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        local_dt = aware_utc_dt.astimezone(colombia_tz)
        return local_dt.strftime('%d-%m-%Y %I:%M %p')
    except Exception:
        return utc_dt.strftime('%Y-%m-%d %H:%M')
    

    
class SavedPostLink(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id", primary_key=True)
    blogpostmodel_id: int = Field(foreign_key="blogpostmodel.id", primary_key=True)

# --- Enumeraciones ---
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class PurchaseStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PENDING_SISTECREDITO_URL = "pending_sistecredito_url"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    FAILED = "failed"
    # --- AÑADE ESTA NUEVA OPCIÓN ---
    DIRECT_SALE = "Venta Directa" 

class VoteType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Category(str, enum.Enum):
    ROPA = "ropa"
    CALZADO = "calzado"
    MOCHILAS = "mochilas"
    OTROS = "otros"

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class UserReputation(str, enum.Enum):
    NONE = "none"
    WOOD = "wood"
    COPPER = "copper"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"

# --- Modelos de Base de Datos ---

class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id", unique=True)
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    
    # --- Campos del Perfil de Usuario ---
    avatar_url: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    
    # --- Campos del Estado del Usuario ---
    is_verified: bool = Field(default=False, nullable=False)
    is_banned: bool = Field(default=False, nullable=False)
    ban_expires_at: Optional[datetime] = Field(default=None)
    
    # --- Campos de Timestamps ---
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)
    
    # --- Campos de Vendedor ---
    seller_barrio: Optional[str] = Field(default=None)
    # --- ✨ ASEGÚRATE DE AÑADIR ESTA LÍNEA SI FALTA ✨ ---
    seller_city: Optional[str] = Field(default=None) 
    seller_address: Optional[str] = Field(default=None)


    # --- Relaciones con otros Modelos ---
    
    # Relación corregida con LocalUser (sin cascada de este lado)
    user: Optional["LocalUser"] = Relationship()

    # Relaciones donde UserInfo es el "padre" (el lado "uno") y debe controlar el borrado
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    shipping_addresses: List["ShippingAddressModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    comments: List["CommentModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    # Relación muchos a muchos para publicaciones guardadas
    saved_posts: List["BlogPostModel"] = Relationship(back_populates="saved_by_users", link_model=SavedPostLink)

    # --- Propiedades Calculadas (no son columnas en la BD) ---

    @property
    def reputation(self) -> UserReputation:
        """Calcula la reputación del usuario basada en los votos de sus comentarios."""
        if not self.comments:
            return UserReputation.NONE

        total_likes = sum(comment.likes for comment in self.comments)
        total_dislikes = sum(comment.dislikes for comment in self.comments)
        like_difference = total_likes - total_dislikes

        if like_difference >= 100:
            return UserReputation.DIAMOND
        elif like_difference >= 30:
            return UserReputation.GOLD
        elif like_difference >= 15:
            return UserReputation.COPPER
        elif like_difference >= 5:
            return UserReputation.WOOD
        else:
            return UserReputation.NONE
            
    @property
    def overall_seller_score(self) -> int:
        """
        Calcula la puntuación promedio del vendedor basada en las
        puntuaciones de todos sus productos que tienen al menos una reseña.
        """
        if not self.posts:
            return 0
        
        scores = [p.seller_score for p in self.posts if p.rating_count > 0]
        
        if not scores:
            return 0

        return round(sum(scores) / len(scores))

    class Config:
        exclude = {"user", "posts", "verification_tokens", "shipping_addresses", "contact_entries", "purchases", "notifications", "comments", "comment_votes", "saved_posts"}

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")
    
    class Config:
        exclude = {"userinfo"}

class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    title: str
    content: str
    price: float = 0.0
    variants: list = Field(default_factory=list, sa_column=Column(JSONB))
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    category: Category = Field(default=Category.OTROS, sa_column=Column(String, nullable=False, server_default=Category.OTROS.value))
    shipping_cost: Optional[float] = Field(default=None)
    is_moda_completa_eligible: bool = Field(default=True, nullable=False)
    combines_shipping: bool = Field(default=False, nullable=False)
    shipping_combination_limit: Optional[int] = Field(default=None)
    price_includes_iva: bool = Field(default=True, nullable=False)
    is_imported: bool = Field(default=False, nullable=False)

    userinfo: "UserInfo" = Relationship(back_populates="posts")
    saved_by_users: List["UserInfo"] = Relationship(back_populates="saved_posts", link_model=SavedPostLink)
    comments: List["CommentModel"] = Relationship(back_populates="blog_post", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    @property
    def base_price(self) -> float:
        if self.price_includes_iva:
            return (self.price or 0.0) / 1.19
        return self.price or 0.0

    @property
    def rating_count(self) -> int:
        if not self.comments: return 0
        return len({c.userinfo_id for c in self.comments})

    @property
    def average_rating(self) -> float:
        if not self.comments: return 0.0
        user_latest_reviews: dict[int, CommentModel] = {}
        for comment in self.comments:
            user_id = comment.userinfo_id
            if user_id not in user_latest_reviews or comment.created_at > user_latest_reviews[user_id].created_at:
                user_latest_reviews[user_id] = comment
        latest_ratings = [review.rating for review in user_latest_reviews.values()]
        if not latest_ratings: return 0.0
        return sum(latest_ratings) / len(latest_ratings)
    
    @property
    def seller_score(self) -> int:
        """Calculates seller score based on comment votes for this post."""
        if not self.comments:
            return 0
        
        total_likes = sum(comment.likes for comment in self.comments)
        total_votes = total_likes + sum(comment.dislikes for comment in self.comments)

        if total_votes == 0:
            return 0
        
        return round((total_likes / total_votes) * 5)


    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)
    @property
    def publish_date_formatted(self) -> str: return format_utc_to_local(self.publish_date)
    @property
    def price_cop(self) -> str: return format_to_cop(self.price)

class ShippingAddressModel(rx.Model, table=True):
    __tablename__ = "shippingaddress"
    userinfo_id: int = Field(foreign_key="userinfo.id")
    name: str; phone: str; city: str; neighborhood: str; address: str
    is_default: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    userinfo: "UserInfo" = Relationship(back_populates="shipping_addresses")

    class Config:
        exclude = {"userinfo"}

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    purchase_date: datetime = Field(default_factory=get_utc_now, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING_PAYMENT, nullable=False) # CAMBIADO a PENDING_PAYMENT por defecto
    shipping_applied: Optional[float] = Field(default=None)
    shipping_name: Optional[str] = None; shipping_city: Optional[str] = None
    shipping_neighborhood: Optional[str] = None; shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    payment_method: str = Field(default="online", nullable=False)
    is_direct_sale: bool = Field(default=False, nullable=False)
    wompi_transaction_id: Optional[str] = Field(default=None, index=True, unique=True)
    wompi_events: list = Field(default_factory=list, sa_column=Column(JSON))
    wompi_payment_link_id: Optional[str] = Field(default=None, index=True)

    # --- INICIO: NUEVOS CAMPOS PARA SISTECREDITO ---
    sistecredito_transaction_id: Optional[str] = Field(default=None, index=True, unique=True)
    sistecredito_authorization_code: Optional[str] = Field(default=None, index=True)
    sistecredito_invoice: Optional[str] = Field(default=None, index=True)
    # --- FIN: NUEVOS CAMPOS PARA SISTECREDITO ---

    estimated_delivery_date: Optional[datetime] = Field(default=None)
    delivery_confirmation_sent_at: Optional[datetime] = Field(default=None)
    user_confirmed_delivery_at: Optional[datetime] = Field(default=None)

    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")

    class Config:
        exclude = {"userinfo", "items"}

    @property
    def purchase_date_formatted(self) -> str: return format_utc_to_local(self.purchase_date)
    @property
    def confirmed_at_formatted(self) -> str: return format_utc_to_local(self.confirmed_at)
    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)
    @property
    def items_formatted(self) -> list[str]:
        if not self.items: return []
        return [f"{item.quantity}x {item.blog_post.title} (a {format_to_cop(item.price_at_purchase)} c/u)" for item in self.items if item.blog_post]

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    quantity: int
    price_at_purchase: float
    selected_variant: dict = Field(default_factory=dict, sa_column=Column(JSON))

    purchase: "PurchaseModel" = Relationship(back_populates="items")
    blog_post: "BlogPostModel" = Relationship()
    comments: List["CommentModel"] = Relationship()

    class Config:
        exclude = {"purchase", "blog_post", "comments"}

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)
    
    userinfo: "UserInfo" = Relationship(back_populates="notifications")
    
    class Config:
        exclude = {"userinfo"}
    
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)

    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")

    class Config:
        exclude = {"userinfo"}

    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class CommentModel(rx.Model, table=True):
    content: str; rating: int
    author_username: str
    author_initial: str
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    parent_comment_id: Optional[int] = Field(default=None, foreign_key="commentmodel.id")
    purchase_item_id: Optional[int] = Field(default=None, foreign_key="purchaseitemmodel.id")
    
    parent: Optional["CommentModel"] = Relationship(back_populates="updates", sa_relationship_kwargs=dict(remote_side="CommentModel.id"))
    updates: List["CommentModel"] = Relationship(back_populates="parent")
    userinfo: "UserInfo" = Relationship(back_populates="comments")
    blog_post: "BlogPostModel" = Relationship(back_populates="comments")
    votes: List["CommentVoteModel"] = Relationship(back_populates="comment")

    class Config:
        exclude = {"blog_post", "userinfo", "parent", "updates", "votes"}

    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)
    @property
    def updated_at_formatted(self) -> str: return format_utc_to_local(self.updated_at)
    @property
    def was_updated(self) -> bool: return (self.updated_at - self.created_at).total_seconds() > 5
    @property
    def likes(self) -> int: return sum(1 for vote in self.votes if vote.vote_type == VoteType.LIKE)
    @property
    def dislikes(self) -> int: return sum(1 for vote in self.votes if vote.vote_type == VoteType.DISLIKE)

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column(String))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    comment_id: int = Field(foreign_key="commentmodel.id")
    
    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    comment: "CommentModel" = Relationship(back_populates="votes")

    class Config:
        exclude = {"userinfo", "comment"}

class SupportTicketModel(rx.Model, table=True):
    """Representa una solicitud de devolución o cambio."""
    purchase_id: int = Field(foreign_key="purchasemodel.id", unique=True) # Solo un ticket por compra
    buyer_id: int = Field(foreign_key="userinfo.id")
    seller_id: int = Field(foreign_key="userinfo.id")
    subject: str
    status: TicketStatus = Field(default=TicketStatus.OPEN, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    purchase: "PurchaseModel" = Relationship(sa_relationship_kwargs={"foreign_keys": "[SupportTicketModel.purchase_id]"})
    buyer: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[SupportTicketModel.buyer_id]"})
    seller: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[SupportTicketModel.seller_id]"})
    messages: List["SupportMessageModel"] = Relationship(back_populates="ticket")

class SupportMessageModel(rx.Model, table=True):
    """Representa un mensaje individual dentro de un ticket de soporte."""
    ticket_id: int = Field(foreign_key="supportticketmodel.id")
    author_id: int = Field(foreign_key="userinfo.id")
    content: str
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    ticket: "SupportTicketModel" = Relationship(back_populates="messages")
    author: "UserInfo" = Relationship()

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)
