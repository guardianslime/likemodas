# likemodas/api/mobile_api.py

import os
import logging
from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional, Dict, Any
from collections import defaultdict
import math
import pytz

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Body, Header, Query
import sqlalchemy
from sqlalchemy.orm import joinedload 
from sqlmodel import select, Session, func
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import (
    BlogPostModel, LocalAuthSession, LocalUser, ReportModel, UserInfo, PurchaseModel, PurchaseItemModel, 
    ShippingAddressModel, SavedPostLink, CommentModel, PurchaseStatus,
    VerificationToken, PasswordResetToken, UserRole, NotificationModel,
    SupportTicketModel, SupportMessageModel
)
from likemodas.services.email_service import send_verification_email, send_password_reset_email
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping
from likemodas.data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES
from likemodas.logic.ranking import get_ranking_query_sort, calculate_review_impact

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com"

# --- DTOs ---

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    token: str

class ProductListDTO(BaseModel):
    id: int
    title: str
    price: float
    price_formatted: str
    image_url: str
    category: str
    description: str
    is_moda_completa: bool
    combines_shipping: bool
    average_rating: float = 0.0
    rating_count: int = 0
    
    # --- CAMPOS DE ESTILO (MODO ARTISTA) ---
    use_default_style: bool = True
    light_mode_appearance: str = "light"
    dark_mode_appearance: str = "dark"
    
    # Colores Hexadecimales
    light_card_bg_color: Optional[str] = None
    light_title_color: Optional[str] = None
    light_price_color: Optional[str] = None
    
    dark_card_bg_color: Optional[str] = None
    dark_title_color: Optional[str] = None
    dark_price_color: Optional[str] = None
    
    # Fondo de imagen (Listado)
    lightbox_bg_light: str = "dark" 
    lightbox_bg_dark: str = "dark"

class VariantDTO(BaseModel):
    id: str
    title: str
    image_url: str
    price: float
    available_quantity: int
    images: List[str]

class ReviewDTO(BaseModel):
    id: int
    username: str
    rating: int
    comment: str
    date: str
    updates: List['ReviewDTO'] = [] 

class ProductDetailDTO(BaseModel):
    id: int
    title: str
    price: float
    price_formatted: str
    description: str
    category: str
    main_image_url: str
    images: List[str]
    variants: List[VariantDTO]
    is_moda_completa: bool
    combines_shipping: bool
    is_saved: bool = False
    is_imported: bool
    average_rating: float = 0.0
    rating_count: int = 0
    reviews: List[ReviewDTO] = [] 
    can_review: bool = False
    author: str
    author_id: int
    created_at: str
    
    # --- CAMPOS DE ESTILO (DETALLE) ---
    # Fondo de imagen (Lightbox)
    lightbox_bg_light: str = "dark"
    lightbox_bg_dark: str = "dark"
    
    # Apariencia de la tarjeta (para etiquetas)
    light_mode_appearance: str = "light"
    dark_mode_appearance: str = "dark"

class ReviewSubmissionBody(BaseModel):
    rating: int
    comment: str
    user_id: int 

class ProfileDTO(BaseModel):
    username: str
    email: str
    phone: str
    avatar_url: str

class PurchaseItemDTO(BaseModel):
    title: str
    quantity: int
    price: float
    image_url: str
    product_id: int
    variant_details: Optional[str] = None

class PurchaseHistoryDTO(BaseModel):
    id: int
    date: str
    status: str
    total: str
    items: List[PurchaseItemDTO]
    estimated_delivery: Optional[str] = None
    can_confirm_delivery: bool = False
    tracking_message: Optional[str] = None
    retry_payment_url: Optional[str] = None
    shipping_name: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_cost: Optional[str] = None
    invoice_path: Optional[str] = None
    return_path: Optional[str] = None
    can_return: bool = False

class InvoiceItemDTO(BaseModel):
    name: str
    quantity: int
    price_unit: str
    total: str
    details: str

class InvoiceDTO(BaseModel):
    id: int
    date: str
    customer_name: str
    customer_address: str
    customer_email: str
    subtotal: str
    shipping: str
    total: str
    items: List[InvoiceItemDTO]

class SupportMessageDTO(BaseModel):
    id: int
    content: str
    is_me: bool
    date: str
    author_name: str

class SupportTicketDTO(BaseModel):
    id: int
    subject: str
    status: str
    messages: List[SupportMessageDTO]

class CreateTicketRequest(BaseModel):
    purchase_id: int
    subject: str
    initial_message: str

class SendMessageRequest(BaseModel):
    ticket_id: int
    content: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class AddressDTO(BaseModel):
    id: int
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool

class CreateAddressRequest(BaseModel):
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool

class CartItemRequest(BaseModel):
    product_id: int
    variant_id: Optional[str] = None
    quantity: int

class CartCalculationRequest(BaseModel):
    items: List[CartItemRequest]

class CartItemResponse(BaseModel):
    product_id: int
    variant_id: Optional[str]
    title: str
    price_formatted: str
    quantity: int
    image_url: str

class CartSummaryResponse(BaseModel):
    subtotal: float
    subtotal_formatted: str
    shipping: float
    shipping_formatted: str
    total: float
    total_formatted: str
    address_id: Optional[int] = None
    items: List[CartItemResponse] = []

class CheckoutRequest(BaseModel):
    items: List[CartItemRequest]
    address_id: int
    payment_method: str

class CheckoutResponse(BaseModel):
    success: bool
    message: str
    payment_url: Optional[str] = None
    purchase_id: Optional[int] = None

class NotificationResponse(BaseModel):
    id: int
    message: str
    url: Optional[str]
    is_read: bool
    created_at: str

# --- AÑADIR ESTE DTO AL PRINCIPIO ---
class ReportRequest(BaseModel):
    target_type: str  # "post" o "comment"
    target_id: int
    reason: str

# --- HELPERS ---

def get_user_info(session: Session, user_id: int) -> UserInfo:
    user_info = session.exec(select(UserInfo).options(joinedload(UserInfo.user)).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info: raise HTTPException(404, "Usuario no encontrado")
    return user_info

def fmt_price(val): 
    if val is None: return "$ 0"
    return f"$ {val:,.0f}".replace(",", ".")

def get_full_image_url(path: str) -> str:
    if not path: return ""
    if path.startswith("http"): return path
    return f"{BASE_URL}/_upload/{path}"

def calculate_rating(session: Session, product_id: int):
    parent_comments = session.exec(select(CommentModel).where(CommentModel.blog_post_id == product_id, CommentModel.parent_comment_id == None).options(joinedload(CommentModel.updates))).unique().all()
    if not parent_comments: return 0.0, 0
    total_rating = 0
    count = len(parent_comments) 
    for parent in parent_comments:
        if parent.updates:
            latest_update = sorted(parent.updates, key=lambda x: x.created_at, reverse=True)[0]
            total_rating += latest_update.rating
        else:
            total_rating += parent.rating
    avg = total_rating / count if count > 0 else 0.0
    return avg, count

def restore_stock_for_failed_purchase(session: Session, purchase: PurchaseModel):
    if not purchase.items: return
    for item in purchase.items:
        if item.blog_post and item.selected_variant:
            current_variants = list(item.blog_post.variants)
            updated = False
            for i, v in enumerate(current_variants):
                if v.get("attributes") == item.selected_variant:
                    new_v = v.copy()
                    new_v["stock"] = new_v.get("stock", 0) + item.quantity
                    current_variants[i] = new_v
                    updated = True
                    break
            if updated:
                item.blog_post.variants = current_variants
                if not item.blog_post.publish_active:
                    total_stock = sum(v.get("stock", 0) for v in item.blog_post.variants)
                    if total_stock > 0:
                        item.blog_post.publish_active = True
                sqlalchemy.orm.attributes.flag_modified(item.blog_post, "variants")
                session.add(item.blog_post)

# --- ENDPOINTS ---

@router.get("/geography/cities", response_model=List[str])
async def get_cities(): return ALL_CITIES

@router.post("/geography/neighborhoods", response_model=List[str])
async def get_neighborhoods(city: str = Body(..., embed=True)): return COLOMBIA_LOCATIONS.get(city, [])

# 1. NUEVA FUNCIÓN DE DEPENDENCIA (Middleware de Seguridad)
# Esta función protege tus endpoints. Verifica que el token enviado en el Header sea válido.
async def get_current_user(
    authorization: str = Header(..., description="Token Bearer"),
    session: Session = Depends(get_session)
) -> UserInfo:
    # Extraer el token del formato "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Formato de token inválido")
    
    token = authorization.split(" ")[1]
    
    # Buscar la sesión en base de datos
    # Nota: Asegúrate de que el modelo LocalAuthSession esté importado de ..models
    auth_session = session.exec(
        select(LocalAuthSession).where(
            LocalAuthSession.session_id == token,
            LocalAuthSession.expiration > datetime.now(timezone.utc)
        )
    ).one_or_none()
    
    if not auth_session:
        raise HTTPException(401, "Sesión expirada o inválida")
        
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == auth_session.user_id)).one()
    return user_info

# 2. LOGIN SEGURO (Generación de Token Real)
@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user: raise HTTPException(404, detail="Usuario no existe")
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): raise HTTPException(400, detail="Contraseña incorrecta")
        
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: raise HTTPException(400, detail="Perfil no encontrado")
        if not user_info.is_verified: raise HTTPException(403, detail="Cuenta no verificada")
        
        # --- CAMBIO DE SEGURIDAD ---
        # Generar un token criptográficamente seguro (48 bytes)
        secure_token = secrets.token_urlsafe(48)
        
        # Guardar la sesión en la base de datos (duración 30 días para móvil)
        new_session = LocalAuthSession(
            user_id=user.id,
            session_id=secure_token,
            expiration=datetime.now(timezone.utc) + timedelta(days=30)
        )
        session.add(new_session)
        session.commit()
        
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        
        # Devolver el token seguro en lugar del ID
        return UserResponse(
            id=user_info.id, 
            username=user.username, 
            email=user_info.email, 
            role=role_str, 
            token=secure_token # <--- Token Real
        )
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(400, detail=str(e))

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first(): raise HTTPException(400, detail="Usuario ya existe")
    try:
        hashed_pw = bcrypt.hashpw(creds.password.encode('utf-8'), bcrypt.gensalt())
        new_user = LocalUser(username=creds.username, password_hash=hashed_pw, enabled=True)
        session.add(new_user); session.commit(); session.refresh(new_user)
        new_info = UserInfo(email=creds.email, user_id=new_user.id, role=UserRole.CUSTOMER, is_verified=False)
        session.add(new_info); session.commit(); session.refresh(new_info)
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        vt = VerificationToken(token=token_str, userinfo_id=new_info.id, expires_at=expires)
        session.add(vt); session.commit()
        try: send_verification_email(recipient_email=creds.email, token=token_str)
        except: pass 
        return UserResponse(id=new_info.id, username=new_user.username, email=new_info.email, role="customer", token=str(new_user.id))
    except Exception as e: raise HTTPException(400, detail=str(e))

@router.post("/forgot-password")
async def mobile_forgot_password(req: ForgotPasswordRequest, session: Session = Depends(get_session)):
    email = req.email.strip().lower()
    user_info = session.exec(select(UserInfo).where(UserInfo.email == email)).one_or_none()
    if user_info:
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        rt = PasswordResetToken(token=token_str, user_id=user_info.user_id, expires_at=expires)
        session.add(rt); session.commit()
        try: send_password_reset_email(recipient_email=email, token=token_str)
        except: pass
    return {"message": "OK"}

@router.get("/products", response_model=List[ProductListDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True)
    if category and category != "todos": query = query.where(BlogPostModel.category == category)
    query = query.order_by(get_ranking_query_sort(BlogPostModel).desc())
    products = session.exec(query).all()
    result = []
    for p in products:
        img_path = p.main_image_url_variant
        
        lightbox_light = "dark"
        lightbox_dark = "dark"
        safe_variants = p.variants if (p.variants and isinstance(p.variants, list)) else []
        if safe_variants:
            first_var = safe_variants[0]
            if isinstance(first_var, dict):
                 lightbox_light = first_var.get("lightbox_bg_light", "dark")
                 lightbox_dark = first_var.get("lightbox_bg_dark", "dark")
        
        if not img_path and safe_variants:
            urls = safe_variants[0].get("image_urls")
            if urls and isinstance(urls, list) and len(urls) > 0: img_path = urls[0]
        
        avg_rating, rating_count = calculate_rating(session, p.id)

        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            average_rating=avg_rating, rating_count=rating_count,
            # MAPEO DE ESTILOS
            use_default_style=p.use_default_style,
            light_mode_appearance=p.light_mode_appearance,
            dark_mode_appearance=p.dark_mode_appearance,
            light_card_bg_color=p.light_card_bg_color,
            light_title_color=p.light_title_color,
            light_price_color=p.light_price_color,
            dark_card_bg_color=p.dark_card_bg_color,
            dark_title_color=p.dark_title_color,
            dark_price_color=p.dark_price_color,
            lightbox_bg_light=lightbox_light,
            lightbox_bg_dark=lightbox_dark
        ))
    return result

@router.get("/products/seller/{seller_id}", response_model=List[ProductListDTO])
async def get_seller_products(seller_id: int, session: Session = Depends(get_session)):
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True, BlogPostModel.userinfo_id == seller_id)
    query = query.order_by(BlogPostModel.created_at.desc())
    products = session.exec(query).all()
    result = []
    for p in products:
        img_path = p.main_image_url_variant
        
        lightbox_light = "dark"
        lightbox_dark = "dark"
        safe_variants = p.variants if (p.variants and isinstance(p.variants, list)) else []
        if safe_variants:
            first_var = safe_variants[0]
            if isinstance(first_var, dict):
                 lightbox_light = first_var.get("lightbox_bg_light", "dark")
                 lightbox_dark = first_var.get("lightbox_bg_dark", "dark")

        if not img_path and safe_variants:
            urls = safe_variants[0].get("image_urls")
            if urls and isinstance(urls, list) and len(urls) > 0: img_path = urls[0]
        
        avg_rating, rating_count = calculate_rating(session, p.id)

        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            average_rating=avg_rating, rating_count=rating_count,
            use_default_style=p.use_default_style,
            light_mode_appearance=p.light_mode_appearance,
            dark_mode_appearance=p.dark_mode_appearance,
            light_card_bg_color=p.light_card_bg_color,
            light_title_color=p.light_title_color,
            light_price_color=p.light_price_color,
            dark_card_bg_color=p.dark_card_bg_color,
            dark_title_color=p.dark_title_color,
            dark_price_color=p.dark_price_color,
            lightbox_bg_light=lightbox_light,
            lightbox_bg_dark=lightbox_dark
        ))
    return result

@router.get("/products/{product_id}", response_model=ProductDetailDTO)
async def get_product_detail(product_id: int, user_id: Optional[int] = None, session: Session = Depends(get_session)):
    try:
        p = session.get(BlogPostModel, product_id)
        if not p or not p.publish_active: raise HTTPException(404, "Producto no encontrado")

        author_name = "Likemodas"
        seller_info_id = p.userinfo_id if p.userinfo_id else 0
        if p.userinfo_id:
            try:
                user_info = session.get(UserInfo, p.userinfo_id)
                if user_info:
                    local_user = session.get(LocalUser, user_info.user_id)
                    if local_user: author_name = local_user.username
                    seller_info_id = user_info.id
            except: pass

        main_img = p.main_image_url_variant
        all_images_set = set()
        safe_variants = p.variants if (p.variants and isinstance(p.variants, list)) else []

        if not main_img and safe_variants:
            first_v_urls = safe_variants[0].get("image_urls")
            if first_v_urls and isinstance(first_v_urls, list) and len(first_v_urls) > 0: main_img = first_v_urls[0]
        if main_img: all_images_set.add(main_img)

        lightbox_light = "dark"
        lightbox_dark = "dark"
        if safe_variants:
            first_var = safe_variants[0]
            if isinstance(first_var, dict):
                lightbox_light = first_var.get("lightbox_bg_light", "dark")
                lightbox_dark = first_var.get("lightbox_bg_dark", "dark")

        for v in safe_variants:
            if isinstance(v, dict):
                urls = v.get("image_urls", [])
                if urls and isinstance(urls, list):
                    for img in urls: 
                        if img: all_images_set.add(img)
        
        final_images = [get_full_image_url(img) for img in all_images_set if img]
        main_image_final = get_full_image_url(main_img or "")
        if not main_image_final and final_images: main_image_final = final_images[0]

        variants_dto = []
        for v in safe_variants:
            if not isinstance(v, dict): continue
            v_urls = v.get("image_urls", [])
            v_img_raw = v_urls[0] if (v_urls and isinstance(v_urls, list) and len(v_urls) > 0) else main_image_final
            v_images_list = [get_full_image_url(img) for img in v_urls if img] if v_urls else [main_image_final]
            attrs = v.get("attributes", {})
            if not isinstance(attrs, dict): attrs = {}
            title_parts = []
            if attrs.get("Color"): title_parts.append(str(attrs.get("Color")))
            if attrs.get("Talla"): title_parts.append(str(attrs.get("Talla")))
            if attrs.get("Número"): title_parts.append(str(attrs.get("Número")))
            v_title = " ".join(title_parts) if title_parts else "Estándar"
            variants_dto.append(VariantDTO(
                id=str(v.get("variant_uuid") or v.get("id") or ""), title=v_title, image_url=get_full_image_url(v_img_raw or ""),
                price=float(v.get("price") or p.price or 0.0), available_quantity=int(v.get("stock") or 0), images=v_images_list
            ))

        reviews_list = []
        db_parent_reviews = session.exec(select(CommentModel).where(CommentModel.blog_post_id == p.id, CommentModel.parent_comment_id == None).order_by(CommentModel.created_at.desc()).options(joinedload(CommentModel.updates))).unique().all()
        for parent in db_parent_reviews:
            updates_dtos = []
            if parent.updates:
                sorted_updates = sorted(parent.updates, key=lambda x: x.created_at, reverse=True)
                for up in sorted_updates: updates_dtos.append(ReviewDTO(id=up.id, username=up.author_username, rating=up.rating, comment=up.content, date=up.created_at.strftime("%d/%m/%Y"), updates=[]))
            reviews_list.append(ReviewDTO(id=parent.id, username=parent.author_username or "Usuario", rating=parent.rating, comment=parent.content, date=parent.created_at.strftime("%d/%m/%Y"), updates=updates_dtos))
        
        avg_rating, rating_count = calculate_rating(session, p.id)
        is_saved, can_review = False, False
        if user_id and user_id > 0:
            try:
                current_user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
                if current_user_info:
                    real_userinfo_id = current_user_info.id
                    saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == real_userinfo_id, SavedPostLink.blogpostmodel_id == p.id)).first()
                    is_saved = saved is not None
                    has_bought = session.exec(select(PurchaseItemModel.id).join(PurchaseModel).where(PurchaseModel.userinfo_id == real_userinfo_id, PurchaseItemModel.blog_post_id == p.id, PurchaseModel.status == PurchaseStatus.DELIVERED)).first()
                    can_review = has_bought is not None
            except Exception: pass

        date_created_str = ""
        try:
            if p.created_at: date_created_str = p.created_at.strftime("%d de %B del %Y")
        except: pass

        return ProductDetailDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            description=p.content, category=p.category, main_image_url=main_image_final, images=final_images, variants=variants_dto,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            is_saved=is_saved, is_imported=p.is_imported, average_rating=avg_rating, rating_count=rating_count, reviews=reviews_list,
            author=author_name, author_id=seller_info_id, created_at=date_created_str, can_review=can_review,
            # MAPEO LIGHTBOX Y APARIENCIA
            lightbox_bg_light=lightbox_light,
            lightbox_bg_dark=lightbox_dark,
            light_mode_appearance=p.light_mode_appearance,
            dark_mode_appearance=p.dark_mode_appearance
        )
    except Exception as e:
        print(f"CRITICAL ERROR 500 product_detail id={product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/cart/checkout/{user_id}", response_model=CheckoutResponse)
async def mobile_checkout(user_id: int, req: CheckoutRequest, session: Session = Depends(get_session)):
    try:
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
        if not user_info: raise HTTPException(404, "Usuario no encontrado")
        address = session.get(ShippingAddressModel, req.address_id)
        if not address or address.userinfo_id != user_info.id: raise HTTPException(400, "Dirección no válida")
        product_ids = [item.product_id for item in req.items]
        db_posts = session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(product_ids)).with_for_update()).all()
        post_map = {p.id: p for p in db_posts}
        subtotal_base = 0.0
        items_to_create = []
        seller_groups = defaultdict(list)
        buyer_city = address.city
        buyer_barrio = address.neighborhood
        for item in req.items:
            post = post_map.get(item.product_id)
            if not post: continue
            post.total_units_sold += item.quantity
            post.last_interaction_at = datetime.now(timezone.utc)
            session.add(post)
            price = post.price
            if not post.price_includes_iva: price = price * 1.19
            subtotal_base += price * item.quantity
            seller_groups[post.userinfo_id].append({"post": post, "qty": item.quantity})
            selected_variant = {}
            if item.variant_id and post.variants:
                target = next((v for v in post.variants if v.get("variant_uuid") == item.variant_id), None)
                if target: selected_variant = target.get("attributes", {})
            items_to_create.append({"blog_post_id": post.id, "quantity": item.quantity, "price_at_purchase": price, "selected_variant": selected_variant})
        subtotal_con_iva = subtotal_base
        free_shipping = False
        moda_items = [p["post"] for uid in seller_groups for p in seller_groups[uid] if p["post"].is_moda_completa_eligible]
        if moda_items:
            thresholds = [p.free_shipping_threshold for p in moda_items if p.free_shipping_threshold]
            if thresholds and subtotal_con_iva >= max(thresholds): free_shipping = True
        final_shipping_cost = 0.0
        if not free_shipping:
            sellers_info = session.exec(select(UserInfo).where(UserInfo.id.in_(seller_groups.keys()))).all()
            seller_map = {u.id: u for u in sellers_info}
            for uid, products in seller_groups.items():
                seller = seller_map.get(uid)
                s_city = seller.seller_city if seller else None
                s_barrio = seller.seller_barrio if seller else None
                combinables = [x["post"] for x in products if x["post"].combines_shipping]
                individuales = [x["post"] for x in products if not x["post"].combines_shipping]
                for p in individuales:
                    cost = calculate_dynamic_shipping(p.shipping_cost or 0, s_barrio, buyer_barrio, s_city, buyer_city)
                    qty = next(x["qty"] for x in products if x["post"].id == p.id)
                    final_shipping_cost += (cost * qty)
                if combinables:
                    base = max((p.shipping_cost or 0 for p in combinables), default=0)
                    cost_group = calculate_dynamic_shipping(base, s_barrio, buyer_barrio, s_city, buyer_city)
                    final_shipping_cost += cost_group
        total_price = subtotal_con_iva + final_shipping_cost
        status = PurchaseStatus.PENDING_PAYMENT if req.payment_method == "Online" else PurchaseStatus.PENDING_CONFIRMATION
        new_purchase = PurchaseModel(userinfo_id=user_info.id, total_price=total_price, shipping_applied=final_shipping_cost, status=status, payment_method=req.payment_method, shipping_name=address.name, shipping_city=address.city, shipping_neighborhood=address.neighborhood, shipping_address=address.address, shipping_phone=address.phone, purchase_date=datetime.now(timezone.utc))
        session.add(new_purchase); session.commit(); session.refresh(new_purchase)
        for item in items_to_create:
            db_item = PurchaseItemModel(purchase_id=new_purchase.id, blog_post_id=item["blog_post_id"], quantity=item["quantity"], price_at_purchase=item["price_at_purchase"], selected_variant=item["selected_variant"])
            session.add(db_item)
        session.commit()
        return CheckoutResponse(success=True, message="OK", purchase_id=new_purchase.id)
    except Exception as e:
        print(f"Checkout error: {e}")
        raise HTTPException(500, f"Error procesando compra: {str(e)}")

@router.post("/cart/calculate/{user_id}", response_model=CartSummaryResponse)
async def calculate_cart(user_id: int, req: CartCalculationRequest, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        default_addr = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id, ShippingAddressModel.is_default == True)).first()
        buyer_city = default_addr.city if default_addr else None
        buyer_barrio = default_addr.neighborhood if default_addr else None
        product_ids = [item.product_id for item in req.items]
        if not product_ids: return CartSummaryResponse(subtotal=0, subtotal_formatted="$ 0", shipping=0, shipping_formatted="$ 0", total=0, total_formatted="$ 0", address_id=default_addr.id if default_addr else None, items=[])
        db_posts = session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(product_ids))).all()
        post_map = {p.id: p for p in db_posts}
        subtotal_base = 0.0
        items_for_shipping = []
        cart_items_response = []
        for item in req.items:
            post = post_map.get(item.product_id)
            if post:
                price = post.price
                if not post.price_includes_iva: price = price * 1.19
                subtotal_base += price * item.quantity
                items_for_shipping.append({"post": post, "quantity": item.quantity})
                variant_image_url = post.main_image_url_variant
                if item.variant_id:
                    target_variant = next((v for v in post.variants if v.get("variant_uuid") == item.variant_id), None)
                    if target_variant and target_variant.get("image_urls"): variant_image_url = target_variant["image_urls"][0]
                if not variant_image_url and post.variants and post.variants[0].get("image_urls"): variant_image_url = post.variants[0]["image_urls"][0]
                cart_items_response.append(CartItemResponse(product_id=post.id, variant_id=item.variant_id, title=post.title, price_formatted=fmt_price(price), quantity=item.quantity, image_url=get_full_image_url(variant_image_url)))
        subtotal_con_iva = subtotal_base
        free_shipping_achieved = False
        moda_completa_items = [x["post"] for x in items_for_shipping if x["post"].is_moda_completa_eligible]
        if moda_completa_items:
            valid_thresholds = [p.free_shipping_threshold for p in moda_completa_items if p.free_shipping_threshold and p.free_shipping_threshold > 0]
            if valid_thresholds and subtotal_con_iva >= max(valid_thresholds): free_shipping_achieved = True
        final_shipping_cost = 0.0
        if not free_shipping_achieved and default_addr:
            seller_groups = defaultdict(list)
            for x in items_for_shipping:
                post = x["post"]
                qty = x["quantity"]
                for _ in range(qty): seller_groups[post.userinfo_id].append(post)
            seller_ids = list(seller_groups.keys())
            sellers_info = session.exec(select(UserInfo).where(UserInfo.id.in_(seller_ids))).all()
            seller_data_map = {info.id: {"city": info.seller_city, "barrio": info.seller_barrio} for info in sellers_info}
            for seller_id, items_from_seller in seller_groups.items():
                combinable_items = [p for p in items_from_seller if p.combines_shipping]
                individual_items = [p for p in items_from_seller if not p.combines_shipping]
                seller_data = seller_data_map.get(seller_id)
                seller_city = seller_data.get("city") if seller_data else None
                seller_barrio = seller_data.get("barrio") if seller_data else None
            
                for individual_item in individual_items:
                    cost = calculate_dynamic_shipping(base_cost=individual_item.shipping_cost or 0.0, seller_barrio=seller_barrio, buyer_barrio=buyer_barrio, seller_city=seller_city, buyer_city=buyer_city)
                    final_shipping_cost += cost
                if combinable_items:
                    highest_base_cost = max((p.shipping_cost or 0.0 for p in combinable_items), default=0.0)
                    limit = min([p.shipping_combination_limit for p in combinable_items if p.shipping_combination_limit and p.shipping_combination_limit > 0] or [1])
                    num_fees = math.ceil(len(combinable_items) / limit)
                    group_shipping_fee = calculate_dynamic_shipping(base_cost=highest_base_cost, seller_barrio=seller_barrio, buyer_barrio=buyer_barrio, seller_city=seller_city, buyer_city=buyer_city)
                    final_shipping_cost += (group_shipping_fee * num_fees)
        grand_total = subtotal_con_iva + final_shipping_cost
        return CartSummaryResponse(subtotal=subtotal_con_iva, subtotal_formatted=fmt_price(subtotal_con_iva), shipping=final_shipping_cost, shipping_formatted=fmt_price(final_shipping_cost), total=grand_total, total_formatted=fmt_price(grand_total), address_id=default_addr.id if default_addr else None, items=cart_items_response)
    except Exception as e:
        print(f"Error calculando carrito: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support/ticket/{purchase_id}/{user_id}", response_model=Optional[SupportTicketDTO])
async def get_support_ticket(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        ticket = session.exec(select(SupportTicketModel).where(SupportTicketModel.purchase_id == purchase_id)).first()
        if not ticket: return None 
        if ticket.buyer_id != user_info.id and ticket.seller_id != user_info.id:
             if user_info.role != UserRole.ADMIN: raise HTTPException(403, "No autorizado")
        messages = session.exec(select(SupportMessageModel).options(joinedload(SupportMessageModel.author).joinedload(UserInfo.user)).where(SupportMessageModel.ticket_id == ticket.id).order_by(SupportMessageModel.created_at)).all()
        msgs_dto = []
        for m in messages:
            author_name = "Usuario"
            if m.author and m.author.user: author_name = m.author.user.username
            date_str = m.created_at.strftime('%d/%m %I:%M %p')
            msgs_dto.append(SupportMessageDTO(id=m.id, content=m.content, is_me=(m.author_id == user_info.id), date=date_str, author_name=author_name))
        return SupportTicketDTO(id=ticket.id, subject=ticket.subject, status=ticket.status.value, messages=msgs_dto)
    except Exception as e: raise HTTPException(500, f"Error interno: {str(e)}")

@router.post("/support/ticket")
async def create_support_ticket(req: CreateTicketRequest, user_id: int = Query(..., alias="user_id"), session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchase = session.exec(select(PurchaseModel).options(joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.id == req.purchase_id)).unique().first()
        if not purchase or purchase.userinfo_id != user_info.id: raise HTTPException(404, "Compra no válida")
        seller_id = None
        if purchase.items:
            for item in purchase.items:
                if item.blog_post: 
                    seller_id = item.blog_post.userinfo_id
                    break
        if not seller_id: 
            admin = session.exec(select(UserInfo).where(UserInfo.role == UserRole.ADMIN)).first()
            seller_id = admin.id if admin else user_info.id
        ticket = SupportTicketModel(purchase_id=purchase.id, buyer_id=user_info.id, seller_id=seller_id, subject=req.subject)
        session.add(ticket); session.commit(); session.refresh(ticket)
        msg = SupportMessageModel(ticket_id=ticket.id, author_id=user_info.id, content=req.initial_message)
        session.add(msg); session.commit()
        note = NotificationModel(userinfo_id=seller_id, message=f"Nueva solicitud de devolución/cambio para la compra #{purchase.id}.", url=f"/returns?purchase_id={purchase.id}")
        session.add(note); session.commit()
        return {"message": "Ticket creado"}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/support/message")
async def send_support_message(req: SendMessageRequest, user_id: int = Query(..., alias="user_id"), session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        ticket = session.get(SupportTicketModel, req.ticket_id)
        if not ticket: raise HTTPException(404, "Ticket no encontrado")
        if user_info.id not in [ticket.buyer_id, ticket.seller_id]:
            if user_info.role != UserRole.ADMIN: raise HTTPException(403, "No autorizado")
        msg = SupportMessageModel(ticket_id=ticket.id, author_id=user_info.id, content=req.content)
        session.add(msg)
        recipient_id = ticket.seller_id if user_info.id == ticket.buyer_id else ticket.buyer_id
        note = NotificationModel(userinfo_id=recipient_id, message=f"Nuevo mensaje en el ticket de la compra #{ticket.purchase_id}", url=f"/returns?purchase_id={ticket.purchase_id}")
        session.add(note); session.commit()
        return {"message": "Enviado"}
    except Exception as e: raise HTTPException(500, str(e))

# 3. EJEMPLO DE ENDPOINT PROTEGIDO (Actualiza tus endpoints críticos así)
@router.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int, 
    current_user: UserInfo = Depends(get_current_user), # <--- Validación automática
    session: Session = Depends(get_session)
):
    # Verificación extra: El usuario logueado solo puede ver SUS notificaciones
    if current_user.id != user_id:
        raise HTTPException(403, "No tienes permiso para ver estos datos")

    notifs = session.exec(select(NotificationModel).where(NotificationModel.userinfo_id == current_user.id).order_by(NotificationModel.created_at.desc()).limit(20)).all()
    # ... (resto de la función igual)
    result = []
    for n in notifs:
        date_str = n.created_at.strftime("%d-%m-%Y %I:%M %p") if n.created_at else ""
        result.append(NotificationResponse(id=n.id, message=n.message, url=n.url, is_read=n.is_read, created_at=date_str))
    return result

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, session: Session = Depends(get_session)):
    notif = session.get(NotificationModel, notification_id)
    if notif:
        notif.is_read = True
        session.add(notif); session.commit()
    return {"message": "Leída"}

@router.delete("/notifications/{user_id}/clear")
async def clear_all_notifications(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    statement = select(NotificationModel).where(NotificationModel.userinfo_id == user_info.id)
    results = session.exec(statement).all()
    for n in results: session.delete(n)
    session.commit()
    return {"message": "Notificaciones eliminadas"}

# --- AÑADIR ESTE ENDPOINT AL FINAL ---
@router.post("/report")
async def create_report(
    req: ReportRequest, 
    session: Session = Depends(get_session), 
    current_user: UserInfo = Depends(get_current_user)
):
    """Recibe un reporte de la App y notifica a los administradores."""
    try:
        # 1. Crear el reporte en la base de datos
        new_report = ReportModel(
            reporter_id=current_user.id,
            target_type=req.target_type,
            target_id=req.target_id,
            reason=req.reason,
            status=ReportStatus.PENDING
        )
        session.add(new_report)
        
        # 2. Buscar a todos los administradores para notificarles
        admins = session.exec(select(UserInfo).where(UserInfo.role == UserRole.ADMIN)).all()
        
        # 3. Crear una notificación (campana) para cada admin
        for admin in admins:
            note = NotificationModel(
                userinfo_id=admin.id,
                # Mensaje corto para la notificación
                message=f"🚨 Nuevo reporte de {req.target_type}: {req.reason[:30]}...",
                url="/admin/reports" # URL de la nueva página de gestión
            )
            session.add(note)
            
        session.commit()
        return {"message": "Reporte recibido. Gracias por ayudarnos a mantener la comunidad segura."}
        
    except Exception as e:
        logger.error(f"Error creando reporte: {e}")
        raise HTTPException(500, "Error interno al procesar el reporte.")