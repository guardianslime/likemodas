import os
import logging
from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional
from collections import defaultdict
import math
import pytz

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Body, Query
import sqlalchemy
from sqlalchemy.orm import joinedload 
from sqlmodel import select, Session
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
        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping
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
        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path or ""), 
            category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping
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

        reviews_list = []
        average_rating = 0.0
        rating_count = 0
        
        try:
            db_reviews = session.exec(select(CommentModel).where(CommentModel.blog_post_id == p.id)).all()
            ratings_sum = 0
            for r in db_reviews:
                try:
                    r_val = r.rating if r.rating is not None else 5
                    ratings_sum += r_val
                    rating_count += 1
                    u_name = r.author_username or "Usuario"
                    content = r.content or ""
                    date_str = r.created_at.strftime("%d/%m/%Y") if r.created_at else ""
                    reviews_list.append(ReviewDTO(
                        id=r.id, username=u_name, rating=int(r_val), comment=content, date=date_str
                    ))
                except: 
                    continue
            if rating_count > 0:
                average_rating = ratings_sum / rating_count
        except:
            pass

        is_saved = False
        can_review = False
        if user_id and user_id > 0:
            try:
                saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_id, SavedPostLink.blogpostmodel_id == p.id)).first()
                is_saved = saved is not None
                has_bought = session.exec(select(PurchaseItemModel.id).join(PurchaseModel).where(PurchaseModel.userinfo_id == user_id, PurchaseItemModel.blogpostmodel_id == p.id)).first()
                already_reviewed = any(r.userinfo_id == user_id for r in db_reviews)
                can_review = (has_bought is not None) and (not already_reviewed)
            except: 
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
            average_rating=average_rating, rating_count=rating_count, reviews=reviews_list,
            author=author_name, author_id=seller_info_id, created_at=date_created_str, can_review=can_review
        )
    except Exception as e:
        print(f"CRITICAL ERROR 500 product_detail id={product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/purchases/{purchase_id}/invoice/{user_id}", response_model=InvoiceDTO)
async def get_mobile_invoice(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        
        purchase = session.exec(
            select(PurchaseModel)
            .options(joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post))
            .where(PurchaseModel.id == purchase_id)
        ).unique().first()
        
        if not purchase: 
            raise HTTPException(404, "Factura no disponible")

        is_buyer = purchase.userinfo_id == user_info.id
        is_seller = False
        
        if purchase.items:
            for item in purchase.items:
                if item.blog_post and item.blog_post.userinfo_id == user_info.id:
                    is_seller = True
                    break
        
        if not is_buyer and not is_seller and user_info.role != UserRole.ADMIN:
            raise HTTPException(403, "No tienes permiso")
            
        items_dto = []
        subtotal_base = 0.0

        if purchase.items:
            for item in purchase.items:
                if item.blog_post:
                    details = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])
                    item_subtotal = item.price_at_purchase * item.quantity
                    subtotal_base += item_subtotal
                    items_dto.append(InvoiceItemDTO(
                        name=item.blog_post.title, quantity=item.quantity,
                        price_unit=fmt_price(item.price_at_purchase),
                        total=fmt_price(item_subtotal), details=details
                    ))
        
        addr = "N/A"
        if purchase.shipping_address:
            parts = []
            if purchase.shipping_address: 
                parts.append(purchase.shipping_address)
            if purchase.shipping_neighborhood: 
                parts.append(purchase.shipping_neighborhood)
            if purchase.shipping_city: 
                parts.append(purchase.shipping_city)
            if parts:
                addr = ", ".join(parts)
        
        return InvoiceDTO(
            id=purchase.id,
            date=purchase.purchase_date.strftime('%d-%m-%Y'),
            customer_name=purchase.shipping_name or "Cliente",
            customer_address=addr,
            customer_email=user_info.email,
            subtotal=fmt_price(subtotal_base),
            shipping=fmt_price(purchase.shipping_applied or 0),
            total=fmt_price(purchase.total_price),
            items=items_dto
        )
    except Exception as e: 
        raise HTTPException(500, str(e))

# --- ENDPOINT DETALLE COMPRA SEGURO Y OPTIMIZADO ---
@router.get("/purchases/{purchase_id}/detail/{user_id}", response_model=PurchaseHistoryDTO)
async def get_mobile_purchase_detail(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        
        # 1. Carga la compra SOLA primero
        purchase = session.get(PurchaseModel, purchase_id)
        if not purchase:
             raise HTTPException(404, "Compra no encontrada")

        # 2. Carga las relaciones necesarias (items y blog_post)
        # Esto evita errores de Lazy Loading en la respuesta.
        session.refresh(purchase, ["items"])
        for item in purchase.items:
            session.refresh(item, ["blog_post"])

        # 3. Validar permisos
        is_buyer = purchase.userinfo_id == user_info.id
        is_seller = False
        
        # Recorrer items de forma segura
        if not is_buyer:
            for item in purchase.items:
                if item.blog_post and item.blog_post.userinfo_id == user_info.id:
                    is_seller = True
                    break
        
        if not is_buyer and not is_seller and user_info.role != UserRole.ADMIN:
             raise HTTPException(403, "No tienes permiso para ver esta compra")

        # 4. Construir DTO
        items_dto = []
        for item in purchase.items:
            img = ""
            # Lógica de imagen defensiva
            if item.blog_post:
                try:
                    variant_img = ""
                    if item.blog_post.variants and item.selected_variant:
                         target_variant = next((v for v in item.blog_post.variants if isinstance(v, dict) and v.get("attributes") == item.selected_variant), None)
                         if target_variant and target_variant.get("image_urls"): 
                             variant_img = target_variant["image_urls"][0]
                    
                    img_path = variant_img or item.blog_post.main_image_url_variant or ""
                    if not img_path and item.blog_post.variants and isinstance(item.blog_post.variants, list):
                         first_v = item.blog_post.variants[0]
                         if isinstance(first_v, dict) and first_v.get("image_urls"): 
                             img_path = first_v["image_urls"][0]
                    img = get_full_image_url(img_path)
                except: 
                    img = ""
            
            variant_str = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])
            items_dto.append(PurchaseItemDTO(
                product_id=item.blog_post_id,
                title=item.blog_post.title if item.blog_post else "Producto Eliminado", 
                quantity=item.quantity, 
                price=item.price_at_purchase, 
                image_url=img,
                variant_details=variant_str
            ))

        sf = f"{purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}" if purchase.shipping_address else "N/A"
        
        return PurchaseHistoryDTO(
            id=purchase.id, 
            date=purchase.purchase_date.strftime('%d-%m-%Y'), 
            status=purchase.status.value, 
            total=fmt_price(purchase.total_price), 
            items=items_dto, 
            estimated_delivery=None, 
            can_confirm_delivery=False, 
            tracking_message=None, 
            retry_payment_url=None, 
            invoice_path=None, 
            can_return=False, 
            shipping_name=purchase.shipping_name, 
            shipping_address=sf, 
            shipping_phone=purchase.shipping_phone, 
            shipping_cost=fmt_price(purchase.shipping_applied or 0.0)
        )

    except Exception as e:
        print(f"Error recuperando detalle de compra {purchase_id}: {e}")
        raise HTTPException(500, f"Error interno al obtener el detalle de la compra: {str(e)}")

@router.get("/support/ticket/{purchase_id}/{user_id}", response_model=Optional[SupportTicketDTO])
async def get_support_ticket(purchase_id: int, user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        
        ticket = session.exec(
            select(SupportTicketModel)
            .where(SupportTicketModel.purchase_id == purchase_id)
        ).first()
        
        if not ticket: 
            return None 
        
        if ticket.buyer_id != user_info.id and ticket.seller_id != user_info.id:
             if user_info.role != UserRole.ADMIN: 
                 raise HTTPException(403, "No autorizado")

        messages = session.exec(
            select(SupportMessageModel)
            .options(joinedload(SupportMessageModel.author).joinedload(UserInfo.user))
            .where(SupportMessageModel.ticket_id == ticket.id)
            .order_by(SupportMessageModel.created_at)
        ).all()
        
        msgs_dto = []
        for m in messages:
            author_name = "Usuario"
            if m.author and m.author.user: 
                author_name = m.author.user.username
            
            date_str = m.created_at.strftime('%d/%m %I:%M %p')
                
            msgs_dto.append(SupportMessageDTO(
                id=m.id, 
                content=m.content, 
                is_me=(m.author_id == user_info.id), 
                date=date_str, 
                author_name=author_name
            ))
            
        return SupportTicketDTO(
            id=ticket.id, 
            subject=ticket.subject, 
            status=ticket.status.value, 
            messages=msgs_dto
        )
    except Exception as e:
        print(f"ERROR GET TICKET: {e}")
        raise HTTPException(500, f"Error interno: {str(e)}")

@router.post("/support/ticket")
async def create_support_ticket(req: CreateTicketRequest, user_id: int = Query(..., alias="user_id"), session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        
        purchase = session.exec(
            select(PurchaseModel)
            .options(joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post))
            .where(PurchaseModel.id == req.purchase_id)
        ).unique().first()
        
        if not purchase or purchase.userinfo_id != user_info.id: 
            raise HTTPException(404, "Compra no válida")
            
        seller_id = None
        if purchase.items:
            for item in purchase.items:
                if item.blog_post: 
                    seller_id = item.blog_post.userinfo_id
                    break
        
        if not seller_id: 
            admin = session.exec(select(UserInfo).where(UserInfo.role == UserRole.ADMIN)).first()
            seller_id = admin.id if admin else user_info.id

        ticket = SupportTicketModel(
            purchase_id=purchase.id, 
            buyer_id=user_info.id, 
            seller_id=seller_id, 
            subject=req.subject
        )
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        
        msg = SupportMessageModel(
            ticket_id=ticket.id, 
            author_id=user_info.id, 
            content=req.initial_message
        )
        session.add(msg)
        session.commit()
        
        note = NotificationModel(
            userinfo_id=seller_id, 
            message=f"Nueva solicitud de devolución/cambio para la compra #{purchase.id}.", 
            url=f"/returns?purchase_id={purchase.id}"
        )
        session.add(note)
        session.commit()

        return {"message": "Ticket creado"}
    except Exception as e:
        print(f"ERROR CREATE TICKET: {e}")
        raise HTTPException(500, str(e))

@router.post("/support/message")
async def send_support_message(req: SendMessageRequest, user_id: int = Query(..., alias="user_id"), session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        ticket = session.get(SupportTicketModel, req.ticket_id)
        
        if not ticket: 
            raise HTTPException(404, "Ticket no encontrado")
        
        if user_info.id not in [ticket.buyer_id, ticket.seller_id]:
            if user_info.role != UserRole.ADMIN: 
                raise HTTPException(403, "No autorizado")
            
        msg = SupportMessageModel(
            ticket_id=ticket.id, 
            author_id=user_info.id, 
            content=req.content
        )
        session.add(msg)
        
        recipient_id = ticket.seller_id if user_info.id == ticket.buyer_id else ticket.buyer_id
        note = NotificationModel(
            userinfo_id=recipient_id, 
            message=f"Nuevo mensaje en el ticket de la compra #{ticket.purchase_id}", 
            url=f"/returns?purchase_id={ticket.purchase_id}"
        )
        session.add(note)
        session.commit()
        
        return {"message": "Enviado"}
    except Exception as e:
        raise HTTPException(500, str(e))