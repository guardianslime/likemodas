import os
import logging
from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional
from collections import defaultdict
import math
import pytz

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Body
import sqlalchemy
from sqlalchemy.orm import joinedload 
from sqlmodel import select, Session
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import (
    BlogPostModel, LocalUser, UserInfo, PurchaseModel, PurchaseItemModel, 
    ShippingAddressModel, SavedPostLink, CommentModel, PurchaseStatus,
    VerificationToken, PasswordResetToken, UserRole, NotificationModel
)
from likemodas.services.email_service import send_verification_email, send_password_reset_email
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping
from likemodas.data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES
from likemodas.services import wompi_service, sistecredito_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
# BASE_URL ahora se usa solo para imágenes, la factura se maneja relativa en la app
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
    
    # Campos de Rastreo y Acción
    estimated_delivery: Optional[str] = None
    can_confirm_delivery: bool = False
    tracking_message: Optional[str] = None
    retry_payment_url: Optional[str] = None
    
    # Campos de Envío (VISIBLES EN LA UI)
    shipping_name: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_cost: Optional[str] = None

    # Campos de Acción Final
    invoice_path: Optional[str] = None  # Cambiado de _url a _path para ser relativo
    return_path: Optional[str] = None   # Nuevo campo para la ruta de devolución
    can_return: bool = False

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
    if not user_info: raise HTTPException(404, "Usuario no encontrado")
    return user_info

def fmt_price(val): 
    if val is None: return "$ 0"
    return f"$ {val:,.0f}".replace(",", ".")

def get_full_image_url(path: str) -> str:
    if not path: return ""
    if path.startswith("http"): return path
    return f"{BASE_URL}/_upload/{path}"

def restore_stock_for_failed_purchase(session: Session, purchase: PurchaseModel):
    """Devuelve el stock al inventario si la compra falla."""
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
        if not user: raise HTTPException(404, detail="Usuario no existe")
        
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): 
            raise HTTPException(400, detail="Contraseña incorrecta")
            
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: raise HTTPException(400, detail="Perfil no encontrado")
        if not user_info.is_verified: raise HTTPException(403, detail="Cuenta no verificada")
        
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        return UserResponse(id=user_info.id, username=user.username, email=user_info.email, role=role_str, token=str(user.id))
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(400, detail=str(e))

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first(): 
        raise HTTPException(400, detail="Usuario ya existe")
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
                    if local_user: author_name = local_user.username
                    seller_info_id = user_info.id
            except: pass

        main_img = p.main_image_url_variant
        all_images_set = set()
        safe_variants = p.variants if (p.variants and isinstance(p.variants, list)) else []

        if not main_img and safe_variants:
            first_v_urls = safe_variants[0].get("image_urls")
            if first_v_urls and isinstance(first_v_urls, list) and len(first_v_urls) > 0:
                main_img = first_v_urls[0]

        if main_img: all_images_set.add(main_img)

        for v in safe_variants:
            if isinstance(v, dict):
                urls = v.get("image_urls", [])
                if urls and isinstance(urls, list):
                    for img in urls: 
                        if img: all_images_set.add(img)
        
        final_images = [get_full_image_url(img) for img in all_images_set if img]
        main_image_final = get_full_image_url(main_img or "")
        if not main_image_final and final_images:
            main_image_final = final_images[0]

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
                except: continue
            
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
            except: pass

        date_created_str = ""
        try:
            if p.created_at: date_created_str = p.created_at.strftime("%d de %B del %Y")
        except: pass

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
            price = post.price
            if not post.price_includes_iva: price *= 1.19
            subtotal_base += price * item.quantity
            
            seller_groups[post.userinfo_id].append({"post": post, "qty": item.quantity})
            
            selected_variant = {}
            if item.variant_id and post.variants:
                target = next((v for v in post.variants if v.get("variant_uuid") == item.variant_id), None)
                if target:
                    current_stock = target.get("stock", 0)
                    if current_stock < item.quantity:
                        raise HTTPException(400, f"Stock insuficiente para {post.title}")
                    
                    new_variants = list(post.variants)
                    for i, v in enumerate(new_variants):
                         if v.get("variant_uuid") == item.variant_id:
                             new_v = v.copy()
                             new_v["stock"] = current_stock - item.quantity
                             new_variants[i] = new_v
                             break
                    post.variants = new_variants
                    sqlalchemy.orm.attributes.flag_modified(post, "variants")
                    
                    total_stock = sum(v.get("stock", 0) for v in post.variants)
                    if total_stock <= 0:
                        post.publish_active = False
                        
                    session.add(post)
                    selected_variant = target.get("attributes", {})
            
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
        
        new_purchase = PurchaseModel(
            userinfo_id=user_info.id, total_price=total_price, shipping_applied=final_shipping_cost, status=status,
            payment_method=req.payment_method, shipping_name=address.name, shipping_city=address.city,
            shipping_neighborhood=address.neighborhood, shipping_address=address.address, shipping_phone=address.phone,
            purchase_date=datetime.now(timezone.utc)
        )
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
                session.add(new_purchase); session.commit()
            else:
                new_purchase.status = PurchaseStatus.FAILED; session.add(new_purchase); session.commit()
                restore_stock_for_failed_purchase(session, new_purchase)
                session.commit()
                raise HTTPException(500, "Error Wompi")

        return CheckoutResponse(success=True, message="OK", payment_url=payment_url, purchase_id=new_purchase.id)

    except Exception as e:
        print(f"Checkout error: {e}")
        raise HTTPException(500, f"Error procesando compra: {str(e)}")

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

@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        purchases = session.exec(
            select(PurchaseModel)
            .options(sqlalchemy.orm.selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post))
            .where(PurchaseModel.userinfo_id == user_info.id)
            .order_by(PurchaseModel.purchase_date.desc())
        ).all()
        
        history = []
        for p in purchases:
            items_dto = []
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
                             if isinstance(first_v, dict) and first_v.get("image_urls"):
                                 img_path = first_v["image_urls"][0]
                        img = get_full_image_url(img_path)
                except: img = ""

                # Detalles de variante
                variant_str = ", ".join([f"{k}: {v}" for k, v in (item.selected_variant or {}).items()])

                items_dto.append(PurchaseItemDTO(
                    product_id=item.blog_post_id,
                    title=item.blog_post.title if item.blog_post else "Producto", 
                    quantity=item.quantity, 
                    price=item.price_at_purchase, 
                    image_url=img,
                    variant_details=variant_str
                ))
            
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
                
                elif p.status == PurchaseStatus.DELIVERED:
                     can_return = True
                     # Usamos rutas relativas para el WebView
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

            history.append(PurchaseHistoryDTO(
                id=p.id, 
                date=p.purchase_date.strftime('%d-%m-%Y'), 
                status=p.status.value, 
                total=fmt_price(p.total_price), 
                items=items_dto, 
                estimated_delivery=estimated_str, 
                can_confirm_delivery=can_confirm, 
                tracking_message=tracking_msg, 
                retry_payment_url=retry_url,
                invoice_path=invoice_path,
                return_path=return_path,
                can_return=can_return,
                shipping_name=p.shipping_name,
                shipping_address=shipping_full_address,
                shipping_phone=p.shipping_phone,
                shipping_cost=fmt_price(p.shipping_applied or 0.0)
            ))
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
        if purchase.status != PurchaseStatus.SHIPPED: raise HTTPException(400, "La compra no está en estado 'Enviado'")
        purchase.status = PurchaseStatus.DELIVERED
        purchase.user_confirmed_delivery_at = datetime.now(timezone.utc)
        session.add(purchase)
        note = NotificationModel(userinfo_id=user_info.id, message=f"Has confirmado la entrega del pedido #{purchase.id}. ¡Gracias!", url="/my-purchases")
        session.add(note)
        session.commit()
        return {"message": "Entrega confirmada exitosamente"}
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(500, str(e))