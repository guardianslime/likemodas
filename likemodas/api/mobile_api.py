import os
import logging
from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional, Dict, Any
from collections import defaultdict
import math
import pytz

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Body, Query
import sqlalchemy
from sqlalchemy.orm import joinedload 
from sqlmodel import select, Session, func
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import (
    BlogPostModel, LocalUser, UserInfo, PurchaseModel, PurchaseItemModel, 
    ShippingAddressModel, SavedPostLink, CommentModel, PurchaseStatus,
    VerificationToken, PasswordResetToken, UserRole, NotificationModel,
    SupportTicketModel, SupportMessageModel, TicketStatus
)
from likemodas.services.email_service import send_verification_email, send_password_reset_email
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping
from likemodas.data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES
from likemodas.services import wompi_service, sistecredito_service

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

class VariantDTO(BaseModel):
    id: str
    title: str
    image_url: str
    price: float
    available_quantity: int
    images: List[str]

# DTO Recursivo para el historial de actualizaciones
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
    image_url: Optional[str] = None 

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

class GenericStatusResponse(BaseModel):
    message: str
    status: Optional[str] = None

class NotificationResponse(BaseModel):
    id: int
    message: str
    url: Optional[str]
    is_read: bool
    created_at: str

# --- HELPERS ---

def get_user_info(session: Session, user_id: int) -> UserInfo:
    user_info = session.exec(
        select(UserInfo)
        .options(joinedload(UserInfo.user))
        .where(UserInfo.user_id == user_id)
    ).one_or_none()
    
    if not user_info: 
        raise HTTPException(404, "Usuario no encontrado")
    return user_info

def fmt_price(val): 
    if val is None: 
        return "$ 0"
    return f"$ {val:,.0f}".replace(",", ".")

def get_full_image_url(path: str) -> str:
    if not path: 
        return ""
    if path.startswith("http"): 
        return path
    return f"{BASE_URL}/_upload/{path}"

def restore_stock_for_failed_purchase(session: Session, purchase: PurchaseModel):
    if not purchase.items:
        return
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

# --- ✅ CÁLCULO DE CALIFICACIÓN CORREGIDO ✅ ---
def calculate_rating(session: Session, product_id: int):
    """
    Calcula el rating tomando solo la ÚLTIMA actualización de cada usuario.
    """
    # 1. Obtener solo los comentarios PADRE (raíz)
    parent_comments = session.exec(
        select(CommentModel)
        .where(CommentModel.blog_post_id == product_id, CommentModel.parent_comment_id == None)
        .options(joinedload(CommentModel.updates))
    ).unique().all()
    
    if not parent_comments:
        return 0.0, 0
    
    total_rating = 0
    count = len(parent_comments) # Cada padre cuenta como 1 usuario único
    
    for parent in parent_comments:
        # 2. Si tiene actualizaciones, usar la calificación de la MÁS RECIENTE
        if parent.updates:
            latest = sorted(parent.updates, key=lambda x: x.created_at, reverse=True)[0]
            total_rating += latest.rating
        else:
            # 3. Si no, usar la del padre
            total_rating += parent.rating
            
    avg = total_rating / count if count > 0 else 0.0
    return avg, count

# --- ENDPOINTS ---

@router.get("/geography/cities", response_model=List[str])
async def get_cities():
    return ALL_CITIES

@router.post("/geography/neighborhoods", response_model=List[str])
async def get_neighborhoods(city: str = Body(..., embed=True)):
    return COLOMBIA_LOCATIONS.get(city, [])

@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user: 
            raise HTTPException(404, detail="Usuario no existe")
        
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): 
            raise HTTPException(400, detail="Contraseña incorrecta")
            
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: 
            raise HTTPException(400, detail="Perfil no encontrado")
        if not user_info.is_verified: 
            raise HTTPException(403, detail="Cuenta no verificada")
        
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        return UserResponse(id=user_info.id, username=user.username, email=user_info.email, role=role_str, token=str(user.id))
    except HTTPException as he: 
        raise he
    except Exception as e: 
        raise HTTPException(400, detail=str(e))

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first(): 
        raise HTTPException(400, detail="Usuario ya existe")
    try:
        hashed_pw = bcrypt.hashpw(creds.password.encode('utf-8'), bcrypt.gensalt())
        new_user = LocalUser(username=creds.username, password_hash=hashed_pw, enabled=True)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
       
        new_info = UserInfo(email=creds.email, user_id=new_user.id, role=UserRole.CUSTOMER, is_verified=False)
        session.add(new_info)
        session.commit()
        session.refresh(new_info)
        
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        vt = VerificationToken(token=token_str, userinfo_id=new_info.id, expires_at=expires)
        session.add(vt)
        session.commit()
        
        try: 
            send_verification_email(recipient_email=creds.email, token=token_str)
        except: 
            pass 
        
        return UserResponse(id=new_info.id, username=new_user.username, email=new_info.email, role="customer", token=str(new_user.id))
    except Exception as e: 
        raise HTTPException(400, detail=str(e))

@router.post("/forgot-password")
async def mobile_forgot_password(req: ForgotPasswordRequest, session: Session = Depends(get_session)):
    email = req.email.strip().lower()
    user_info = session.exec(select(UserInfo).where(UserInfo.email == email)).one_or_none()
    if user_info:
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        rt = PasswordResetToken(token=token_str, user_id=user_info.user_id, expires_at=expires)
        session.add(rt)
        session.commit()
        try: 
            send_password_reset_email(recipient_email=email, token=token_str)
        except: 
            pass
    return {"message": "OK"}

@router.get("/products", response_model=List[ProductListDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True)
    if category and category != "todos": 
        query = query.where(BlogPostModel.category == category)
    query = query.order_by(BlogPostModel.created_at.desc())
    products = session.exec(query).all()
    result = []
    for p in products:
        img_path = p.main_image_url_variant
        if not img_path:
            if p.variants and isinstance(p.variants, list) and len(p.variants) > 0:
                urls = p.variants[0].get("image_urls")
                if urls and isinstance(urls, list) and len(urls) > 0:
                    img_path = urls[0]
        
        avg_rating, rating_count = calculate_rating(session, p.id)

        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            average_rating=avg_rating, rating_count=rating_count
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
        if not img_path:
            if p.variants and isinstance(p.variants, list) and len(p.variants) > 0:
                urls = p.variants[0].get("image_urls")
                if urls and isinstance(urls, list) and len(urls) > 0:
                    img_path = urls[0]

        avg_rating, rating_count = calculate_rating(session, p.id)

        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            average_rating=avg_rating, rating_count=rating_count
        ))
    return result

@router.get("/products/{product_id}", response_model=ProductDetailDTO)
async def get_product_detail(product_id: int, user_id: Optional[int] = None, session: Session = Depends(get_session)):
    try:
        p = session.get(BlogPostModel, product_id)
        if not p or not p.publish_active:
            raise HTTPException(404, "Producto no encontrado")

        author_name = "Likemodas"
        seller_info_id = p.userinfo_id if p.userinfo_id else 0
        if p.userinfo_id:
            try:
                user_info = session.get(UserInfo, p.userinfo_id)
                if user_info:
                    local_user = session.get(LocalUser, user_info.user_id)
                    if local_user: 
                        author_name = local_user.username
                    seller_info_id = user_info.id
            except: 
                pass

        main_img = p.main_image_url_variant
        all_images_set = set()
        safe_variants = p.variants if (p.variants and isinstance(p.variants, list)) else []

        if not main_img and safe_variants:
            first_v_urls = safe_variants[0].get("image_urls")
            if first_v_urls and isinstance(first_v_urls, list) and len(first_v_urls) > 0:
                main_img = first_v_urls[0]

        if main_img: 
            all_images_set.add(main_img)

        for v in safe_variants:
            if isinstance(v, dict):
                urls = v.get("image_urls", [])
                if urls and isinstance(urls, list):
                    for img in urls: 
                        if img: 
                            all_images_set.add(img)
        
        final_images = [get_full_image_url(img) for img in all_images_set if img]
        main_image_final = get_full_image_url(main_img or "")
        if not main_image_final and final_images:
            main_image_final = final_images[0]

        variants_dto = []
        for v in safe_variants:
            if not isinstance(v, dict): 
                continue
            
            v_urls = v.get("image_urls", [])
            v_img_raw = v_urls[0] if (v_urls and isinstance(v_urls, list) and len(v_urls) > 0) else main_image_final
            v_images_list = [get_full_image_url(img) for img in v_urls if img] if v_urls else [main_image_final]
            
            attrs = v.get("attributes", {})
            if not isinstance(attrs, dict): 
                attrs = {}
            
            title_parts = []
            if attrs.get("Color"): 
                title_parts.append(str(attrs.get("Color")))
            if attrs.get("Talla"): 
                title_parts.append(str(attrs.get("Talla")))
            if attrs.get("Número"): 
                title_parts.append(str(attrs.get("Número")))
            
            v_title = " ".join(title_parts) if title_parts else "Estándar"

            variants_dto.append(VariantDTO(
                id=str(v.get("variant_uuid") or v.get("id") or ""),
                title=v_title,
                image_url=get_full_image_url(v_img_raw or ""),
                price=float(v.get("price") or p.price or 0.0),
                available_quantity=int(v.get("stock") or 0),
                images=v_images_list
            ))

        # --- REVIEWS ESTRUCTURADAS (Padre -> Hijos) ---
        reviews_list = []
        
        # 1. Obtener padres (comentarios raíz)
        db_parent_reviews = session.exec(
            select(CommentModel)
            .where(CommentModel.blog_post_id == p.id, CommentModel.parent_comment_id == None)
            .order_by(CommentModel.created_at.desc())
            .options(joinedload(CommentModel.updates))
        ).unique().all()
        
        for parent in db_parent_reviews:
            updates_dtos = []
            if parent.updates:
                # 2. Ordenar actualizaciones (hijos)
                sorted_updates = sorted(parent.updates, key=lambda x: x.created_at, reverse=True)
                for up in sorted_updates:
                    updates_dtos.append(ReviewDTO(
                        id=up.id,
                        username=up.author_username,
                        rating=up.rating,
                        comment=up.content,
                        date=up.created_at.strftime("%d/%m/%Y"),
                        updates=[] 
                    ))

            # 3. Empaquetar padre con sus hijos
            reviews_list.append(ReviewDTO(
                id=parent.id,
                username=parent.author_username or "Usuario",
                rating=parent.rating,
                comment=parent.content,
                date=parent.created_at.strftime("%d/%m/%Y"),
                updates=updates_dtos # <--- Aquí van los hijos
            ))
            
        avg_rating, rating_count = calculate_rating(session, p.id)

        # ✅ CORRECCIÓN DE LA VARIABLE is_saved:
        is_saved = False # Se define al inicio, siempre tendrá valor.
        can_review = False
        
        if user_id and user_id > 0:
            try:
                current_user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
                if current_user_info:
                    real_userinfo_id = current_user_info.id
                    
                    saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == real_userinfo_id, SavedPostLink.blogpostmodel_id == p.id)).first()
                    is_saved = saved is not None
                    
                    # Verificar compra entregada
                    has_bought = session.exec(
                        select(PurchaseItemModel.id)
                        .join(PurchaseModel)
                        .where(
                            PurchaseModel.userinfo_id == real_userinfo_id, 
                            PurchaseItemModel.blog_post_id == p.id,
                            PurchaseModel.status == PurchaseStatus.DELIVERED
                        )
                    ).first()
                    can_review = has_bought is not None
            except Exception as e:
                pass

        date_created_str = ""
        try:
            if p.created_at: 
                date_created_str = p.created_at.strftime("%d de %B del %Y")
        except: 
            pass

        return ProductDetailDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            description=p.content, category=p.category,
            main_image_url=main_image_final, images=final_images, variants=variants_dto,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            is_saved=is_saved, is_imported=p.is_imported, 
            average_rating=avg_rating, rating_count=rating_count, reviews=reviews_list,
            author=author_name, author_id=seller_info_id, created_at=date_created_str, can_review=can_review
        )
    except Exception as e:
        print(f"CRITICAL ERROR 500 product_detail id={product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/products/{product_id}/reviews")
async def create_product_review(product_id: int, body: ReviewSubmissionBody, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == body.user_id)).one_or_none()
    if not user_info:
        raise HTTPException(404, "Usuario no encontrado")

    purchase_item = session.exec(
        select(PurchaseItemModel)
        .join(PurchaseModel)
        .where(
            PurchaseModel.userinfo_id == user_info.id,
            PurchaseItemModel.blog_post_id == product_id,
            PurchaseModel.status == PurchaseStatus.DELIVERED
        )
        .order_by(PurchaseModel.purchase_date.desc())
    ).first()

    if not purchase_item:
        raise HTTPException(400, "Debes haber comprado y recibido este producto para opinar.")

    # Verificar si ya existe el PADRE
    existing_comment = session.exec(
        select(CommentModel)
        .where(
            CommentModel.purchase_item_id == purchase_item.id,
            CommentModel.parent_comment_id == None
        )
    ).one_or_none()

    if existing_comment:
        update_count = session.exec(
            select(func.count(CommentModel.id))
            .where(CommentModel.parent_comment_id == existing_comment.id)
        ).one()

        if update_count >= 3:
            raise HTTPException(400, "Has alcanzado el límite de 3 actualizaciones para esta compra.")

        new_update = CommentModel(
            content=body.comment,
            rating=body.rating,
            author_username=user_info.user.username,
            author_initial=user_info.user.username[0].upper(),
            userinfo_id=user_info.id,
            blog_post_id=product_id,
            purchase_item_id=purchase_item.id,
            parent_comment_id=existing_comment.id
        )
        session.add(new_update)
        session.commit()
        return {"message": "Opinión actualizada exitosamente"}
    else:
        new_comment = CommentModel(
            content=body.comment,
            rating=body.rating,
            author_username=user_info.user.username,
            author_initial=user_info.user.username[0].upper(),
            userinfo_id=user_info.id,
            blog_post_id=product_id,
            purchase_item_id=purchase_item.id,
            parent_comment_id=None
        )
        session.add(new_comment)
        session.commit()
        return {"message": "Opinión creada exitosamente"}

# ... (El resto de endpoints Invoice, Support, etc. se mantienen igual que tu versión funcional) ...
@router.get("/purchases/{purchase_id}/invoice/{user_id}", response_model=InvoiceDTO)
async def get_mobile_invoice(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchase = session.exec(select(PurchaseModel).options(joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.id == purchase_id)).unique().first()
        if not purchase: raise HTTPException(404, "Factura no disponible")
        is_buyer = purchase.userinfo_id == user_info.id
        is_seller = False
        if purchase.items:
            for item in purchase.items:
                if item.blog_post and item.blog_post.userinfo_id == user_info.id:
                    is_seller = True
                    break
        if not is_buyer and not is_seller and user_info.role != UserRole.ADMIN: raise HTTPException(403, "No tienes permiso")
        items_dto = []
        subtotal_base = 0.0
        if purchase.items:
            for item in purchase.items:
                if item.blog_post:
                    details = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])
                    item_subtotal = item.price_at_purchase * item.quantity
                    subtotal_base += item_subtotal
                    items_dto.append(InvoiceItemDTO(name=item.blog_post.title, quantity=item.quantity, price_unit=fmt_price(item.price_at_purchase), total=fmt_price(item_subtotal), details=details))
        addr = "N/A"
        if purchase.shipping_address:
            parts = []
            if purchase.shipping_address: parts.append(purchase.shipping_address)
            if purchase.shipping_neighborhood: parts.append(purchase.shipping_neighborhood)
            if purchase.shipping_city: parts.append(purchase.shipping_city)
            if parts: addr = ", ".join(parts)
        return InvoiceDTO(id=purchase.id, date=purchase.purchase_date.strftime('%d-%m-%Y'), customer_name=purchase.shipping_name or "Cliente", customer_address=addr, customer_email=user_info.email, subtotal=fmt_price(subtotal_base), shipping=fmt_price(purchase.shipping_applied or 0), total=fmt_price(purchase.total_price), items=items_dto)
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/purchases/{purchase_id}/detail/{user_id}", response_model=PurchaseHistoryDTO)
async def get_mobile_purchase_detail(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchase = session.exec(select(PurchaseModel).options(joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.id == purchase_id)).unique().first()
        if not purchase: raise HTTPException(404, "Compra no encontrada")
        is_buyer = purchase.userinfo_id == user_info.id
        is_seller = False
        if not is_buyer and purchase.items:
             for item in purchase.items:
                 if item.blog_post and item.blog_post.userinfo_id == user_info.id:
                     is_seller = True
                     break
        if not is_buyer and not is_seller and user_info.role != UserRole.ADMIN: raise HTTPException(403, "No tienes permiso para ver esta compra")
        items_dto = []
        if purchase.items:
            for item in purchase.items:
                img = ""
                title = "Producto no disponible" 
                if item.blog_post:
                    title = item.blog_post.title
                    try:
                        variant_img = ""
                        if item.blog_post.variants and item.selected_variant:
                            target_variant = next((v for v in item.blog_post.variants if isinstance(v, dict) and v.get("attributes") == item.selected_variant), None)
                            if target_variant and target_variant.get("image_urls"): variant_img = target_variant["image_urls"][0]
                        img_path = variant_img or item.blog_post.main_image_url_variant or ""
                        if not img_path and item.blog_post.variants and isinstance(item.blog_post.variants, list):
                            first_v = item.blog_post.variants[0]
                            if isinstance(first_v, dict) and first_v.get("image_urls"): img_path = first_v["image_urls"][0]
                        img = get_full_image_url(img_path)
                    except: img = ""
                variant_str = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])
                items_dto.append(PurchaseItemDTO(product_id=item.blog_post_id, title=title, quantity=item.quantity, price=item.price_at_purchase, image_url=img, variant_details=variant_str))
        sf = f"{purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}" if purchase.shipping_address else "N/A"
        return PurchaseHistoryDTO(id=purchase.id, date=purchase.purchase_date.strftime('%d-%m-%Y'), status=purchase.status.value, total=fmt_price(purchase.total_price), items=items_dto, estimated_delivery=None, can_confirm_delivery=False, tracking_message=None, retry_payment_url=None, invoice_path=None, can_return=False, shipping_name=purchase.shipping_name, shipping_address=sf, shipping_phone=purchase.shipping_phone, shipping_cost=fmt_price(purchase.shipping_applied or 0.0))
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(404, f"No se pudo cargar el detalle: {str(e)}")

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
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        msg = SupportMessageModel(ticket_id=ticket.id, author_id=user_info.id, content=req.initial_message)
        session.add(msg)
        session.commit()
        note = NotificationModel(userinfo_id=seller_id, message=f"Nueva solicitud de devolución/cambio para la compra #{purchase.id}.", url=f"/returns?purchase_id={purchase.id}")
        session.add(note)
        session.commit()
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
        session.add(note)
        session.commit()
        return {"message": "Enviado"}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/cart/checkout/{user_id}", response_model=CheckoutResponse)
async def mobile_checkout(user_id: int, req: CheckoutRequest, session: Session = Depends(get_session)):
    try:
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
        if not user_info: raise HTTPException(404, "Usuario no encontrado")
        address = session.get(ShippingAddressModel, req.address_id)
        if not address or address.userinfo_id != user_info.id: raise HTTPException(400, "Dirección no válida")
        product_ids = [item.product_id for item in req.items]
        db_posts = session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(product_ids))).all()
        post_map = {p.id: p for p in db_posts}
        subtotal_base = 0.0
        items_to_create = []
        seller_groups = defaultdict(list)
        buyer_city = address.city
        buyer_barrio = address.neighborhood
        for item in req.items:
            post = post_map.get(item.product_id)
            if not post: continue
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
        session.add(new_purchase)
        session.commit()
        session.refresh(new_purchase)
        for item in items_to_create:
            db_item = PurchaseItemModel(purchase_id=new_purchase.id, blog_post_id=item["blog_post_id"], quantity=item["quantity"], price_at_purchase=item["price_at_purchase"], selected_variant=item["selected_variant"])
            session.add(db_item)
        session.commit()
        payment_url = None
        if req.payment_method == "Online":
            link_tuple = await wompi_service.create_wompi_payment_link(new_purchase.id, total_price)
            if link_tuple:
                payment_url, link_id = link_tuple
                new_purchase.wompi_payment_link_id = link_id
                session.add(new_purchase)
                session.commit()
            else:
                new_purchase.status = PurchaseStatus.FAILED
                session.add(new_purchase)
                session.commit()
                raise HTTPException(500, "Error Wompi")
        return CheckoutResponse(success=True, message="OK", payment_url=payment_url, purchase_id=new_purchase.id)
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

@router.post("/products/{product_id}/toggle-save/{user_id}")
async def toggle_save_product(product_id: int, user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    existing = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_info.id, SavedPostLink.blogpostmodel_id == product_id)).first()
    if existing:
        session.delete(existing)
        session.commit()
        return {"message": "Producto eliminado de guardados", "is_saved": False}
    else:
        new_saved = SavedPostLink(userinfo_id=user_info.id, blogpostmodel_id=product_id)
        session.add(new_saved)
        session.commit()
        return {"message": "Producto guardado", "is_saved": True}

@router.get("/profile/{user_id}", response_model=ProfileDTO)
async def get_mobile_profile(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    local_user = session.get(LocalUser, user_id)
    avatar = get_full_image_url(user_info.avatar_url)
    return ProfileDTO(username=local_user.username if local_user else "Usuario", email=user_info.email, phone=user_info.phone or "", avatar_url=avatar)

@router.put("/profile/{user_id}")
async def update_mobile_profile(user_id: int, phone: str, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    user_info.phone = phone
    session.add(user_info)
    session.commit()
    return {"message": "Perfil actualizado"}

@router.get("/addresses/{user_id}", response_model=List[AddressDTO])
async def get_addresses(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    addresses = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id).order_by(ShippingAddressModel.is_default.desc())).all()
    return [AddressDTO(id=a.id, name=a.name, phone=a.phone, city=a.city, neighborhood=a.neighborhood, address=a.address, is_default=a.is_default) for a in addresses]

@router.post("/addresses/{user_id}")
async def create_address(user_id: int, req: CreateAddressRequest, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    if req.is_default:
        existing = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).all()
        for addr in existing: 
            addr.is_default = False
            session.add(addr)
    count = session.exec(select(sqlalchemy.func.count()).select_from(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).one()
    is_def = req.is_default or (count == 0)
    new_addr = ShippingAddressModel(userinfo_id=user_info.id, name=req.name, phone=req.phone, city=req.city, neighborhood=req.neighborhood, address=req.address, is_default=is_def)
    session.add(new_addr)
    session.commit()
    return {"message": "Dirección guardada"}

@router.put("/addresses/{user_id}/set_default/{address_id}")
async def set_default_address(user_id: int, address_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    existing = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).all()
    for addr in existing: 
        addr.is_default = False
        session.add(addr)
    target = session.get(ShippingAddressModel, address_id)
    if target and target.userinfo_id == user_info.id:
        target.is_default = True
        session.add(target)
        session.commit()
        return {"message": "Dirección actualizada"}
    raise HTTPException(404, "Dirección no encontrada")

@router.post("/profile/{user_id}/change-password")
async def change_password(user_id: int, req: ChangePasswordRequest, session: Session = Depends(get_session)):
    user = session.get(LocalUser, user_id)
    if not user: raise HTTPException(404, "Usuario no encontrado")
    if not bcrypt.checkpw(req.current_password.encode('utf-8'), user.password_hash): raise HTTPException(400, "Contraseña actual incorrecta")
    user.password_hash = bcrypt.hashpw(req.new_password.encode('utf-8'), bcrypt.gensalt())
    session.add(user)
    session.commit()
    return {"message": "Contraseña actualizada"}

@router.get("/profile/{user_id}/saved-posts", response_model=List[ProductListDTO])
async def get_saved_posts(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    user_with_posts = session.exec(select(UserInfo).options(sqlalchemy.orm.selectinload(UserInfo.saved_posts)).where(UserInfo.id == user_info.id)).one()
    saved_posts = user_with_posts.saved_posts
    result = []
    for p in saved_posts:
        if not p.publish_active: continue
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        avg_rating, rating_count = calculate_rating(session, p.id)
        result.append(ProductListDTO(id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price), image_url=get_full_image_url(img_path), category=p.category, description=p.content, is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping, average_rating=avg_rating, rating_count=rating_count))
    return result

@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchases = session.exec(select(PurchaseModel).options(sqlalchemy.orm.selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post)).where(PurchaseModel.userinfo_id == user_info.id).order_by(PurchaseModel.purchase_date.desc())).all()
        history = []
        for p in purchases:
            try:
                items_dto = []
                if p.items:
                    for item in p.items:
                        img = ""
                        try:
                            if item.blog_post:
                                variant_img = ""
                                if item.blog_post.variants and item.selected_variant:
                                     target_variant = next((v for v in item.blog_post.variants if isinstance(v, dict) and v.get("attributes") == item.selected_variant), None)
                                     if target_variant and target_variant.get("image_urls"): variant_img = target_variant["image_urls"][0]
                                img_path = variant_img or item.blog_post.main_image_url_variant or ""
                                if not img_path and item.blog_post.variants and isinstance(item.blog_post.variants, list):
                                     first_v = item.blog_post.variants[0]
                                     if isinstance(first_v, dict) and first_v.get("image_urls"): img_path = first_v["image_urls"][0]
                                img = get_full_image_url(img_path)
                        except: img = ""
                        variant_str = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])
                        items_dto.append(PurchaseItemDTO(product_id=item.blog_post_id, title=item.blog_post.title if item.blog_post else "Producto", quantity=item.quantity, price=item.price_at_purchase, image_url=img, variant_details=variant_str))
                estimated_str = None
                can_confirm = False
                can_return = False
                tracking_msg = None
                retry_url = None
                invoice_path = None
                return_path = None
                try:
                    if p.status == PurchaseStatus.SHIPPED:
                        can_confirm = True
                        if p.estimated_delivery_date:
                            local_dt = p.estimated_delivery_date.replace(tzinfo=timezone.utc).astimezone(pytz.timezone("America/Bogota"))
                            estimated_str = local_dt.strftime('%d-%m-%Y %I:%M %p')
                            tracking_msg = f"Llega aprox: {estimated_str}"
                        else:
                            tracking_msg = "Tu pedido llegará pronto."
                    elif p.status == PurchaseStatus.DELIVERED:
                         can_return = True
                         invoice_path = f"/invoice?id={p.id}"
                         return_path = f"/returns?purchase_id={p.id}"
                    elif p.status == PurchaseStatus.PENDING_CONFIRMATION:
                         tracking_msg = "Esperando confirmación del vendedor"
                    elif p.status == PurchaseStatus.PENDING_PAYMENT and p.payment_method == "Online":
                        time_diff = datetime.now(timezone.utc) - p.purchase_date
                        if time_diff > timedelta(minutes=15):
                            p.status = PurchaseStatus.FAILED
                            restore_stock_for_failed_purchase(session, p)
                            session.add(p)
                            session.commit()
                        elif p.wompi_payment_link_id:
                            retry_url = f"https://checkout.wompi.co/l/{p.wompi_payment_link_id}"
                except: tracking_msg = ""
                shipping_full_address = f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}" if p.shipping_address else "N/A"
                history.append(PurchaseHistoryDTO(id=p.id, date=p.purchase_date.strftime('%d-%m-%Y'), status=p.status.value, total=fmt_price(p.total_price), items=items_dto, estimated_delivery=estimated_str, can_confirm_delivery=can_confirm, tracking_message=tracking_msg, retry_payment_url=retry_url, invoice_path=invoice_path, return_path=return_path, can_return=can_return, shipping_name=p.shipping_name, shipping_address=shipping_full_address, shipping_phone=p.shipping_phone, shipping_cost=fmt_price(p.shipping_applied or 0.0)))
            except Exception as e:
                print(f"Error procesando compra {p.id}: {e}")
                continue
        return history
    except Exception as e:
        print(f"ERROR CRÍTICO EN PURCHASES: {e}")
        return []

@router.post("/purchases/{purchase_id}/confirm-delivery/{user_id}")
async def confirm_delivery_mobile(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchase = session.get(PurchaseModel, purchase_id)
        if not purchase or purchase.userinfo_id != user_info.id: raise HTTPException(404, "Compra no encontrada")
        purchase.status = PurchaseStatus.DELIVERED
        purchase.user_confirmed_delivery_at = datetime.now(timezone.utc)
        session.add(purchase)
        note = NotificationModel(userinfo_id=user_info.id, message=f"Has confirmado la entrega del pedido #{purchase.id}. ¡Gracias!", url="/my-purchases")
        session.add(note)
        session.commit()
        return {"message": "Entrega confirmada exitosamente"}
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/purchases/confirm_wompi_transaction")
async def confirm_wompi_transaction(transaction_id: str = Body(..., embed=True), session: Session = Depends(get_session)):
    try:
        tx_data = await wompi_service.get_wompi_transaction_details(transaction_id)
        if not tx_data: raise HTTPException(404, "Transacción no encontrada")
        status = tx_data.get("status")
        payment_link_id = tx_data.get("payment_link_id")
        if not payment_link_id: raise HTTPException(400, "No hay link de pago")
        purchase = session.exec(select(PurchaseModel).where(PurchaseModel.wompi_payment_link_id == payment_link_id)).one_or_none()
        if not purchase: raise HTTPException(404, "Compra no encontrada")
        if status == "APPROVED":
            if purchase.status != PurchaseStatus.CONFIRMED:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                purchase.wompi_transaction_id = transaction_id
                session.add(purchase)
                note = NotificationModel(userinfo_id=purchase.userinfo_id, message=f"¡Pago confirmado! Tu orden #{purchase.id} ha sido procesada.", url="/my-purchases")
                session.add(note)
                session.commit()
                return {"message": "Pago confirmado", "status": "confirmed"}
            else: return {"message": "Ya confirmado", "status": "confirmed"}
        elif status in ["DECLINED", "ERROR", "VOIDED"]:
             if purchase.status == PurchaseStatus.PENDING_PAYMENT:
                 purchase.status = PurchaseStatus.FAILED
                 restore_stock_for_failed_purchase(session, purchase)
                 session.add(purchase)
                 session.commit()
             return {"message": "Pago rechazado", "status": "failed"}
        return {"message": f"Estado: {status}", "status": "pending"}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/purchases/{purchase_id}/verify_payment")
async def verify_payment_mobile(purchase_id: int, session: Session = Depends(get_session)):
    try:
        purchase = session.get(PurchaseModel, purchase_id)
        if not purchase: raise HTTPException(404, "Orden no encontrada")
        if purchase.status != PurchaseStatus.PENDING_PAYMENT: return {"message": "Orden procesada", "status": purchase.status}
        transaction = await wompi_service.get_transaction_by_reference(str(purchase.id))
        if transaction:
            status = transaction.get("status")
            if status == "APPROVED":
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                purchase.wompi_transaction_id = transaction.get("id")
                session.add(purchase)
                session.commit()
                return {"message": "Confirmado", "status": "confirmed"}
            elif status in ["DECLINED", "ERROR", "VOIDED"]:
                 purchase.status = PurchaseStatus.FAILED
                 restore_stock_for_failed_purchase(session, purchase)
                 session.add(purchase)
                 session.commit()
                 return {"message": "Fallido", "status": "failed"}
        return {"message": "Pendiente", "status": "pending"}
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_notifications(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    notifs = session.exec(select(NotificationModel).where(NotificationModel.userinfo_id == user_info.id).order_by(NotificationModel.created_at.desc()).limit(20)).all()
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
        session.add(notif)
        session.commit()
    return {"message": "Leída"}

@router.delete("/notifications/{user_id}/clear")
async def clear_all_notifications(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    statement = select(NotificationModel).where(NotificationModel.userinfo_id == user_info.id)
    results = session.exec(statement).all()
    for n in results: session.delete(n)
    session.commit()
    return {"message": "Notificaciones eliminadas"}