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
# from .utils.formatting import format_to_cop

# --- Adelanta la declaración de modelos ---
if "CommentModel" not in locals():
    CommentModel = "CommentModel"
if "PurchaseItemModel" not in locals():
    PurchaseItemModel = "PurchaseItemModel"

def _format_to_cop_backend(value: float | None) -> str:
    """
    Función de formato PRIVADA. Solo para el backend (modelos y DTOs).
    """
    if value is None or value < 1:
        return "$ 0"
    formatted_number = f"{value:,.0f}"
    colombian_format = formatted_number.replace(',', '.')
    return f"$ {colombian_format}"

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
# --- 1. MODIFICAR UserRole ---
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    VENDEDOR = "vendedor"  # <-- AÑADIR ESTA LÍNEA

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

# Añadir este enum
class GastoCategoria(str, enum.Enum):
    MARKETING = "Marketing"
    SOFTWARE = "Software"
    COMISIONES = "Comisiones"
    LOGISTICA = "Logística"
    SUMINISTROS = "Suministros"
    OTROS = "Otros"

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

# --- REEMPLAZA LA CLASE EmploymentRequest ---
class EmploymentRequest(rx.Model, table=True):
    """Guarda una solicitud de empleo de un Vendedor a un Candidato."""
    __tablename__ = "employmentrequest"
    
    requester_id: int = Field(foreign_key="userinfo.id")
    candidate_id: int = Field(foreign_key="userinfo.id")
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    requester_username: str

    requester: "UserInfo" = Relationship(back_populates="solicitudes_enviadas", sa_relationship_kwargs={"foreign_keys": "[EmploymentRequest.requester_id]"})
    candidate: "UserInfo" = Relationship(back_populates="solicitudes_recibidas", sa_relationship_kwargs={"foreign_keys": "[EmploymentRequest.candidate_id]"})

    # --- ✨ CORRECCIÓN AQUÍ: AÑADE ESTA NUEVA PROPIEDAD ✨ ---
    @property
    def created_at_formatted(self) -> str:
        """Devuelve la fecha de creación formateada."""
        return format_utc_to_local(self.created_at)

# --- 2. AÑADIR EL NUEVO MODELO EmpleadoVendedorLink ---
class EmpleadoVendedorLink(rx.Model, table=True):
    """
    Tabla de enlace que establece la relación jerárquica 
    entre un Vendedor y un Empleado.
    """
    __tablename__ = "empleadovendedorlink"

    vendedor_id: int = Field(foreign_key="userinfo.id")
    # La restricción de unicidad garantiza que un empleado solo tiene un empleador
    empleado_id: int = Field(foreign_key="userinfo.id", unique=True)
    
    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )
    
    # Relaciones para facilitar las consultas con SQLModel
    vendedor: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[EmpleadoVendedorLink.vendedor_id]"})
    empleado: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[EmpleadoVendedorLink.empleado_id]"})


# --- Modelos de Base de Datos ---

# --- REEMPLAZA LA CLASE UserInfo ---
class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id", unique=True)
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    
    # ... (todos tus otros campos como avatar_url, phone, is_verified, etc. se mantienen igual)
    avatar_url: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False, nullable=False)
    is_banned: bool = Field(default=False, nullable=False)
    ban_expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)
    seller_barrio: Optional[str] = Field(default=None)
    seller_city: Optional[str] = Field(default=None) 
    seller_address: Optional[str] = Field(default=None)
    tfa_secret: Optional[str] = Field(default=None)
    tfa_enabled: bool = Field(default=False, nullable=False)

    # --- Relaciones con otros Modelos (la mayoría se mantienen igual) ---
    user: Optional["LocalUser"] = Relationship()
    posts: List["BlogPostModel"] = Relationship(
        back_populates="userinfo",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[BlogPostModel.userinfo_id]"  # <--- ¡LÍNEA CLAVE AÑADIDA!
        }
    )
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    shipping_addresses: List["ShippingAddressModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    # Versión corregida, especificando la clave foránea:
    purchases: List["PurchaseModel"] = Relationship(
        back_populates="userinfo",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[PurchaseModel.userinfo_id]"
        }
    )
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    comments: List["CommentModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    saved_posts: List["BlogPostModel"] = Relationship(back_populates="saved_by_users", link_model=SavedPostLink)
    gastos: List["Gasto"] = Relationship(
        back_populates="userinfo",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[Gasto.userinfo_id]"
        }
    )

    # Relaciones de Empleado/Vendedor (se mantienen igual)
    empleados: List["EmpleadoVendedorLink"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "UserInfo.id==EmpleadoVendedorLink.vendedor_id",
            "cascade": "all, delete-orphan",
            # ✨ AÑADE ESTA LÍNEA PARA RESOLVER LA ADVERTENCIA ✨
            "overlaps": "empleado,vendedor",
        }
    )
    empleador_link: Optional["EmpleadoVendedorLink"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "UserInfo.id==EmpleadoVendedorLink.empleado_id",
            "uselist": False,
            # ✨ AÑADE ESTA LÍNEA PARA RESOLVER LA ADVERTENCIA ✨
            "overlaps": "empleado,vendedor",
        }
    )

    # --- ✨ NUEVAS RELACIONES AÑADIDAS AQUÍ ✨ ---
    # Estas son las relaciones inversas que faltaban
    solicitudes_enviadas: List["EmploymentRequest"] = Relationship(back_populates="requester", sa_relationship_kwargs={"foreign_keys": "[EmploymentRequest.requester_id]"})
    solicitudes_recibidas: List["EmploymentRequest"] = Relationship(back_populates="candidate", sa_relationship_kwargs={"foreign_keys": "[EmploymentRequest.candidate_id]"})


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

    userinfo_id: int = Field(foreign_key="userinfo.id") # Dueño
    creator_id: Optional[int] = Field(default=None, foreign_key="userinfo.id") # Creador (empleado)
    
    last_modified_by_id: Optional[int] = Field(default=None, foreign_key="userinfo.id") # Quien lo modificó por última vez
    # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

    # --- ✨ ASEGÚRATE DE TENER ESTA RELACIÓN ✨ ---
    last_modified_by: Optional["UserInfo"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[BlogPostModel.last_modified_by_id]"})
    # --- ✨ FIN ✨ ---
    
    title: str
    content: str
    price: float = 0.0
    profit: Optional[float] = Field(default=None)
    variants: list = Field(default_factory=list, sa_column=Column(JSONB))
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    category: Category = Field(default=Category.OTROS, sa_column=Column(String, nullable=False, server_default=Category.OTROS.value))
    attr_material: Optional[str] = Field(default=None)

# --- ✨ INICIO: AÑADE ESTA LÍNEA ✨ ---
    attr_tipo: Optional[str] = Field(default=None)

    shipping_cost: Optional[float] = Field(default=None)
    is_moda_completa_eligible: bool = Field(default=True, nullable=False)

    # ✨ --- INICIO: AÑADE ESTE NUEVO CAMPO --- ✨
    free_shipping_threshold: Optional[float] = Field(default=None)
    # ✨ --- FIN: AÑADE ESTE NUEVO CAMPO --- ✨

    combines_shipping: bool = Field(default=False, nullable=False)
    shipping_combination_limit: Optional[int] = Field(default=None)
    price_includes_iva: bool = Field(default=True, nullable=False)
    is_imported: bool = Field(default=False, nullable=False)

    # --- SECCIÓN DE ESTILOS ---
    use_default_style: bool = Field(default=True, nullable=False)

    # Nuevo campo para la inversión del tema
    card_theme_invert: bool = Field(default=False, nullable=False) # <--- AÑADE ESTA LÍNEA

    # Colores para el modo claro (Estos se quedan)
    light_card_bg_color: Optional[str] = Field(default=None)
    light_title_color: Optional[str] = Field(default=None)
    light_price_color: Optional[str] = Field(default=None)

    # Colores para el modo oscuro (Estos se quedan)
    dark_card_bg_color: Optional[str] = Field(default=None)
    dark_title_color: Optional[str] = Field(default=None)
    dark_price_color: Optional[str] = Field(default=None)

    # Dentro de BlogPostModel
    light_mode_appearance: str = Field(default="light", nullable=False) # Opciones: "light", "dark"
    dark_mode_appearance: str = Field(default="dark", nullable=False)  # Opciones: "light", "dark"

    # El estilo de imagen se mantiene
    image_styles: Optional[dict] = Field(default_factory=dict)
    # --- ✨ INICIO: AÑADE ESTA LÍNEA ✨ ---
    main_image_url_variant: Optional[str] = Field(default=None)

    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # Le decimos a la relación 'userinfo' (el dueño) que se vincule a través de 'userinfo_id'
    userinfo: "UserInfo" = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={"foreign_keys": "[BlogPostModel.userinfo_id]"} # <--- ¡LÍNEA CLAVE AÑADIDA!
    )
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
    # --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
    # Relación para poder cargar los datos del creador fácilmente
    creator: Optional["UserInfo"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[BlogPostModel.creator_id]"})
    # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---
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
    def price_cop(self) -> str: 
        # 👇 CAMBIA LA LLAMADA a la nueva función
        return _format_to_cop_backend(self.price)

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

    action_by_id: Optional[int] = Field(default=None, foreign_key="userinfo.id") # El último usuario (vendedor/empleado) que actuó sobre el pedido

    # --- ✨ INICIO: AÑADE ESTE NUEVO CAMPO ✨ ---
    anonymous_customer_email: Optional[str] = Field(default=None, index=True)
    # --- ✨ FIN: AÑADE ESTE NUEVO CAMPO ✨ ---

    action_by: Optional["UserInfo"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[PurchaseModel.action_by_id]"})

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
    # --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
    actual_shipping_cost: Optional[float] = Field(default=None)
    # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

    # --- INICIO: NUEVOS CAMPOS PARA SISTECREDITO ---
    sistecredito_transaction_id: Optional[str] = Field(default=None, index=True, unique=True)
    sistecredito_authorization_code: Optional[str] = Field(default=None, index=True)
    sistecredito_invoice: Optional[str] = Field(default=None, index=True)
    # --- FIN: NUEVOS CAMPOS PARA SISTECREDITO ---

    estimated_delivery_date: Optional[datetime] = Field(default=None)
    delivery_confirmation_sent_at: Optional[datetime] = Field(default=None)
    user_confirmed_delivery_at: Optional[datetime] = Field(default=None)

    userinfo: "UserInfo" = Relationship(
        back_populates="purchases",
        sa_relationship_kwargs={"foreign_keys": "[PurchaseModel.userinfo_id]"}
    )
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")

    class Config:
        exclude = {"userinfo", "items"}

    @property
    def purchase_date_formatted(self) -> str: return format_utc_to_local(self.purchase_date)
    
    @property
    def confirmed_at_formatted(self) -> str: return format_utc_to_local(self.confirmed_at)
    
    @property
    def total_price_cop(self) -> str: 
        # 👇 CAMBIA LA LLAMADA a la nueva función
        return _format_to_cop_backend(self.total_price)
    

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


class Gasto(rx.Model, table=True):
    """Representa un gasto operativo registrado por un administrador."""
    userinfo_id: int = Field(foreign_key="userinfo.id") # El dueño del gasto (el Vendedor)
    creator_id: Optional[int] = Field(default=None, foreign_key="userinfo.id") # Quien lo registró (el Empleado)
    fecha: datetime = Field(default_factory=get_utc_now, nullable=False)
    descripcion: str
    categoria: GastoCategoria = Field(default=GastoCategoria.OTROS, nullable=False)
    valor: float

    userinfo: "UserInfo" = Relationship(
        back_populates="gastos",
        sa_relationship_kwargs={"foreign_keys": "[Gasto.userinfo_id]"}
    )

    # --- ✨ ASEGÚRATE DE TENER ESTA RELACIÓN ✨ ---
    creator: Optional["UserInfo"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Gasto.creator_id]"})
    # --- ✨ FIN ✨ -

    @property
    def fecha_formateada(self) -> str:
        return format_utc_to_local(self.fecha)

    @property
    def valor_cop(self) -> str:
        # 👇 CAMBIA LA LLAMADA a la nueva función
        return _format_to_cop_backend(self.valor)

class ActivityLog(rx.Model, table=True):
    """Registra una acción realizada por un usuario en el panel."""
    # Quién realizó la acción (el empleado o el vendedor)
    actor_id: int = Field(foreign_key="userinfo.id")
    # A qué vendedor pertenecen los datos afectados
    owner_id: int = Field(foreign_key="userinfo.id")
    
    action_type: str  # Ej: "Creación de Publicación", "Edición de Gasto"
    description: str  # Ej: "Creó la publicación 'Camisa a Rayas'"
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    actor: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[ActivityLog.actor_id]"})
    owner: "UserInfo" = Relationship(sa_relationship_kwargs={"foreign_keys": "[ActivityLog.owner_id]"})

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)