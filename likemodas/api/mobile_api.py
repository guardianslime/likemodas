import os
import logging
from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional
from collections import defaultdict
import math

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Body
import sqlalchemy
from sqlalchemy.orm import joinedload 
from sqlmodel import select, Session
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import (
    BlogPostModel, LocalUser, PasswordResetToken, UserInfo, PurchaseModel, PurchaseItemModel, 
    ShippingAddressModel, SavedPostLink, CommentModel, PurchaseStatus, UserRole, VerificationToken
)
from likemodas.services import wompi_service 
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping
from likemodas.data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES
from likemodas.services.email_service import send_password_reset_email, send_verification_email

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
    
    # Campos calculados manualmente para evitar Error 500
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

class PurchaseHistoryDTO(BaseModel):
    id: int
    date: str
    status: str
    total: str
    items: List[PurchaseItemDTO]

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
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): raise HTTPException(400, detail="Contraseña incorrecta")
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: raise HTTPException(400, detail="Perfil no encontrado")
        if not user_info.is_verified: raise HTTPException(403, detail="Cuenta no verificada")
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        return UserResponse(id=user_info.id, username=user.username, email=user_info.email, role=role_str, token=str(user.id))
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

# --- ENDPOINT CRÍTICO CORREGIDO: NO USA p.average_rating ---
@router.get("/products/{product_id}", response_model=ProductDetailDTO)
async def get_product_detail(product_id: int, user_id: Optional[int] = None, session: Session = Depends(get_session)):
    try:
        # 1. Obtener producto (Sin joins complejos iniciales)
        p = session.get(BlogPostModel, product_id)
        if not p or not p.publish_active: 
            raise HTTPException(404, "Producto no encontrado")

        # 2. Obtener Autor con consulta separada (Seguro)
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

        # 3. Imágenes
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

        # 4. OPINIONES (MANUAL): Consultamos la tabla explícitamente
        reviews_list = []
        average_rating = 0.0
        rating_count = 0
        
        # Consulta separada a CommentModel
        db_reviews = session.exec(select(CommentModel).where(CommentModel.blog_post_id == p.id)).all()
        
        ratings = [r.rating for r in db_reviews if r.rating is not None]
        rating_count = len(ratings)
        average_rating = (sum(ratings) / rating_count) if rating_count > 0 else 0.0
        
        for r in db_reviews:
            try:
                date_str = r.created_at.strftime("%d/%m/%Y") if r.created_at else ""
                u_name = r.author_username or "Usuario"
                r_val = r.rating or 5
                content = r.content or ""
                reviews_list.append(ReviewDTO(id=r.id, username=u_name, rating=int(r_val), comment=content, date=date_str))
            except: continue

        is_saved = False
        can_review = False
        if user_id and user_id > 0:
            saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_id, SavedPostLink.blogpostmodel_id == p.id)).first()
            is_saved = saved is not None
            has_bought = session.exec(select(PurchaseItemModel.id).join(PurchaseModel).where(PurchaseModel.userinfo_id == user_id, PurchaseItemModel.blogpostmodel_id == p.id)).first()
            already_reviewed = any(r.userinfo_id == user_id for r in db_reviews)
            can_review = (has_bought is not None) and (not already_reviewed)

        date_created_str = p.created_at.strftime("%d de %B del %Y") if p.created_at else ""

        return ProductDetailDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            description=p.content, category=p.category,
            main_image_url=main_image_final, images=final_images, variants=variants_dto,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            is_saved=is_saved, is_imported=p.is_imported, 
            
            # Usamos valores calculados manualmente
            average_rating=average_rating, 
            rating_count=rating_count,
            reviews=reviews_list,
            
            author=author_name, author_id=seller_info_id, created_at=date_created_str, can_review=can_review
        )
    except Exception as e:
        print(f"CRITICAL ERROR 500 product_detail id={product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# --- CHECKOUT ---
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
            if not post.price_includes_iva: price *= 1.19
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
                raise HTTPException(500, "Error Wompi")

        return CheckoutResponse(success=True, message="OK", payment_url=payment_url, purchase_id=new_purchase.id)

    except Exception as e:
        print(f"CHECKOUT ERROR: {e}")
        raise HTTPException(500, str(e))

# ... (Resto de endpoints: reviews, toggle-save, etc)
@router.post("/products/{product_id}/reviews")
async def create_product_review(product_id: int, body: ReviewSubmissionBody, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, body.user_id)
        purchase_item = session.exec(select(PurchaseItemModel).join(PurchaseModel).where(PurchaseModel.userinfo_id == user_info.id, PurchaseItemModel.blogpostmodel_id == product_id)).first()
        if not purchase_item: raise HTTPException(400, "Debes comprar para opinar.")
        
        existing = session.exec(select(CommentModel.id).where(CommentModel.userinfo_id == user_info.id, CommentModel.blog_post_id == product_id)).first()
        if existing: raise HTTPException(400, "Ya opinaste.")
        
        username = "Usuario"
        initial = "U"
        if user_info.user:
            username = user_info.user.username
            initial = username[0].upper()

        new_review = CommentModel(
            userinfo_id=user_info.id, blog_post_id=product_id, rating=body.rating, content=body.comment,
            author_username=username, author_initial=initial, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
            purchase_item_id=purchase_item.id
        )
        session.add(new_review)
        session.commit()
        return {"message": "Opinión guardada"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/products/{product_id}/toggle-save/{user_id}")
async def toggle_save_product(product_id: int, user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    existing = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_info.id, SavedPostLink.blogpostmodel_id == product_id)).first()
    if existing:
        session.delete(existing); session.commit()
        return {"message": "Producto eliminado de guardados", "is_saved": False}
    else:
        new_saved = SavedPostLink(userinfo_id=user_info.id, blogpostmodel_id=product_id)
        session.add(new_saved); session.commit()
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
    session.add(user_info); session.commit()
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
        for addr in existing: addr.is_default = False; session.add(addr)
    count = session.exec(select(sqlalchemy.func.count()).select_from(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).one()
    is_def = req.is_default or (count == 0)
    new_addr = ShippingAddressModel(userinfo_id=user_info.id, name=req.name, phone=req.phone, city=req.city, neighborhood=req.neighborhood, address=req.address, is_default=is_def)
    session.add(new_addr); session.commit()
    return {"message": "Dirección guardada"}

@router.put("/addresses/{user_id}/set_default/{address_id}")
async def set_default_address(user_id: int, address_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    existing = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).all()
    for addr in existing: addr.is_default = False; session.add(addr)
    target = session.get(ShippingAddressModel, address_id)
    if target and target.userinfo_id == user_info.id:
        target.is_default = True; session.add(target); session.commit()
        return {"message": "Dirección actualizada"}
    raise HTTPException(404, "Dirección no encontrada")

@router.post("/profile/{user_id}/change-password")
async def change_password(user_id: int, req: ChangePasswordRequest, session: Session = Depends(get_session)):
    user = session.get(LocalUser, user_id)
    if not user: raise HTTPException(404, "Usuario no encontrado")
    if not bcrypt.checkpw(req.current_password.encode('utf-8'), user.password_hash): raise HTTPException(400, "Contraseña actual incorrecta")
    user.password_hash = bcrypt.hashpw(req.new_password.encode('utf-8'), bcrypt.gensalt())
    session.add(user); session.commit()
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
        result.append(ProductListDTO(id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price), image_url=get_full_image_url(img_path), category=p.category, description=p.content, is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping))
    return result

@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    purchases = session.exec(select(PurchaseModel).options(sqlalchemy.orm.selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post)).where(PurchaseModel.userinfo_id == user_info.id).order_by(PurchaseModel.purchase_date.desc())).all()
    history = []
    for p in purchases:
        items_dto = []
        for item in p.items:
            img = ""
            if item.blog_post:
                variant_img = ""
                if item.blog_post.variants and item.selected_variant:
                     target_variant = next((v for v in item.blog_post.variants if v.get("attributes") == item.selected_variant), None)
                     if target_variant and target_variant.get("image_urls"): variant_img = target_variant["image_urls"][0]
                img_path = variant_img or item.blog_post.main_image_url_variant or (item.blog_post.variants[0]["image_urls"][0] if item.blog_post.variants and item.blog_post.variants[0].get("image_urls") else "")
                img = get_full_image_url(img_path)
            items_dto.append(PurchaseItemDTO(title=item.blog_post.title if item.blog_post else "Producto", quantity=item.quantity, price=item.price_at_purchase, image_url=img))
        history.append(PurchaseHistoryDTO(id=p.id, date=p.purchase_date.strftime('%d-%m-%Y'), status=p.status.value, total=fmt_price(p.total_price), items=items_dto))
    return history

@router.post("/cart/calculate/{user_id}", response_model=CartSummaryResponse)
async def calculate_cart(user_id: int, req: CartCalculationRequest, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, user_id)
        default_addr = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id, ShippingAddressModel.is_default == True)).first()
        buyer_city = default_addr.city if default_addr else None
        buyer_barrio = default_addr.neighborhood if default_addr else None
        product_ids = [item.product_id for item in req.items]
        if not product_ids: return CartSummaryResponse(subtotal=0, subtotal_formatted="$ 0", shipping=0, shipping_formatted="$ 0", total=0, total_formatted="$ 0", address_id=default_addr.id if default_addr else None)
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
                post = x["post"]; qty = x["quantity"]
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