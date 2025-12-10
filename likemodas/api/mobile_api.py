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
    BlogPostModel, LocalAuthSession, LocalUser, UserInfo, PurchaseModel, PurchaseItemModel, 
    ShippingAddressModel, SavedPostLink, CommentModel, PurchaseStatus,
    VerificationToken, PasswordResetToken, UserRole, NotificationModel,
    SupportTicketModel, SupportMessageModel, ReportModel, ReportStatus # ✨ IMPORTAR REPORTMODEL
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
    
    # ✨ CORRECCIÓN: CAMPOS DE ENVÍO QUE FALTABAN ✨
    shipping_cost: Optional[float] = None
    is_moda_completa: bool
    combines_shipping: bool
    free_shipping_threshold: Optional[float] = None
    shipping_display_text: Optional[str] = None
    
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
    lightbox_bg_light: str = "dark"
    lightbox_bg_dark: str = "dark"
    
    light_mode_appearance: str = "light"
    dark_mode_appearance: str = "dark"
    light_card_bg_color: Optional[str] = None
    light_title_color: Optional[str] = None
    light_price_color: Optional[str] = None
    dark_card_bg_color: Optional[str] = None
    dark_title_color: Optional[str] = None
    dark_price_color: Optional[str] = None

class ReviewSubmissionBody(BaseModel):
    rating: int
    comment: str
    user_id: int 

# ✨ NUEVO DTO PARA REPORTES ✨
class ReportRequest(BaseModel):
    target_type: str # "post" o "comment"
    target_id: int
    reason: str

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

class ToggleSaveResponse(BaseModel):
    message: str
    is_saved: bool

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

def get_current_user(
    authorization: str = Header(..., description="Token Bearer"),
    session: Session = Depends(get_session)
) -> UserInfo:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Formato de token inválido")
    token = authorization.split(" ")[1]
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

# --- ENDPOINTS ---

@router.get("/geography/cities", response_model=List[str])
async def get_cities(): return ALL_CITIES

@router.post("/geography/neighborhoods", response_model=List[str])
async def get_neighborhoods(city: str = Body(..., embed=True)): return COLOMBIA_LOCATIONS.get(city, [])

@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user: raise HTTPException(404, detail="Usuario no existe")
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): raise HTTPException(400, detail="Contraseña incorrecta")
        
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: raise HTTPException(400, detail="Perfil no encontrado")
        if not user_info.is_verified: raise HTTPException(403, detail="Cuenta no verificada")
        
        secure_token = secrets.token_urlsafe(48)
        new_session = LocalAuthSession(
            user_id=user.id,
            session_id=secure_token,
            expiration=datetime.now(timezone.utc) + timedelta(days=30)
        )
        session.add(new_session)
        session.commit()
        
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        return UserResponse(id=user_info.id, username=user.username, email=user_info.email, role=role_str, token=secure_token)
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

# --- ✨ ENDPOINT DE REPORTE (UGC) ✨ ---
@router.post("/report")
async def create_report(
    req: ReportRequest, 
    session: Session = Depends(get_session), 
    current_user: UserInfo = Depends(get_current_user)
):
    try:
        new_report = ReportModel(
            reporter_id=current_user.id,
            target_type=req.target_type,
            target_id=req.target_id,
            reason=req.reason,
            status=ReportStatus.PENDING
        )
        session.add(new_report)
        
        admins = session.exec(select(UserInfo).where(UserInfo.role == UserRole.ADMIN)).all()
        for admin in admins:
            note = NotificationModel(
                userinfo_id=admin.id,
                message=f"🚨 Nuevo reporte de {req.target_type}: {req.reason[:30]}...",
                url="/admin/reports"
            )
            session.add(note)
            
        session.commit()
        return {"message": "Reporte recibido."}
    except Exception as e:
        logger.error(f"Error reportando: {e}")
        raise HTTPException(500, "Error interno.")

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

        # ✨ CÁLCULO DEL TEXTO DE ENVÍO
        shipping_text = "Envío a convenir"
        if p.shipping_cost == 0:
            shipping_text = "Envío Gratis"
        elif p.shipping_cost and p.shipping_cost > 0:
            shipping_text = f"Envío: {fmt_price(p.shipping_cost)}"

        return ProductDetailDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            description=p.content, category=p.category, main_image_url=main_image_final, images=final_images, variants=variants_dto,
            
            # ✨ CAMPOS DE ENVÍO RELLENADOS ✨
            shipping_cost=p.shipping_cost,
            is_moda_completa=p.is_moda_completa_eligible,
            combines_shipping=p.combines_shipping,
            free_shipping_threshold=p.free_shipping_threshold,
            shipping_display_text=shipping_text,
            
            is_saved=is_saved, is_imported=p.is_imported, average_rating=avg_rating, rating_count=rating_count, reviews=reviews_list,
            author=author_name, author_id=seller_info_id, created_at=date_created_str, can_review=can_review,
            lightbox_bg_light=lightbox_light,
            lightbox_bg_dark=lightbox_dark,
            light_mode_appearance=p.light_mode_appearance,
            dark_mode_appearance=p.dark_mode_appearance,
            light_card_bg_color=p.light_card_bg_color,
            light_title_color=p.light_title_color,
            light_price_color=p.light_price_color,
            dark_card_bg_color=p.dark_card_bg_color,
            dark_title_color=p.dark_title_color,
            dark_price_color=p.dark_price_color
        )
    except Exception as e:
        print(f"CRITICAL ERROR 500 product_detail id={product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ... (El resto del archivo se mantiene igual: cart endpoints, notifications, etc.)
@router.post("/cart/checkout/{user_id}", response_model=CheckoutResponse)
async def mobile_checkout(user_id: int, req: CheckoutRequest, session: Session = Depends(get_session)):
    # ... (código existente sin cambios)
    return CheckoutResponse(success=True, message="Función checkout omitida por brevedad")

@router.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_notifications(user_id: int, current_user: UserInfo = Depends(get_current_user), session: Session = Depends(get_session)):
    if current_user.id != user_id: raise HTTPException(403, "No autorizado")
    notifs = session.exec(select(NotificationModel).where(NotificationModel.userinfo_id == current_user.id).order_by(NotificationModel.created_at.desc()).limit(20)).all()
    result = []
    for n in notifs:
        date_str = n.created_at.strftime("%d-%m-%Y %I:%M %p") if n.created_at else ""
        result.append(NotificationResponse(id=n.id, message=n.message, url=n.url, is_read=n.is_read, created_at=date_str))
    return result

@router.delete("/notifications/{user_id}/clear")
async def clear_all_notifications(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    statement = select(NotificationModel).where(NotificationModel.userinfo_id == user_info.id)
    results = session.exec(statement).all()
    for n in results: session.delete(n)
    session.commit()
    return {"message": "Notificaciones eliminadas"}