import os
import bcrypt
import secrets
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
import sqlalchemy
from sqlmodel import select, Session
from pydantic import BaseModel

# Asegúrate de tener estas importaciones
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken, PurchaseModel, PurchaseItemModel, ShippingAddressModel, SavedPostLink, CommentModel
from likemodas.services.email_service import send_verification_email, send_password_reset_email
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping
from likemodas.data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com"

# --- DTOs (Modelos de Datos) ---
# ... (Mantén LoginRequest, RegisterRequest, etc. igual que antes) ...
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

# --- NUEVOS DTOs PARA OPINIONES ---
class ReviewDTO(BaseModel):
    id: int
    username: str
    rating: int
    comment: str
    date: str

class ReviewSubmissionBody(BaseModel):
    rating: int
    comment: str
    user_id: int

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
    # Campos para opiniones
    average_rating: float = 0.0
    rating_count: int = 0
    reviews: List[ReviewDTO] = [] 
    can_review: bool = False
    # Autor
    author: str
    author_id: int
    created_at: str

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

# --- HELPERS ---
def get_user_info(session: Session, user_id: int) -> UserInfo:
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info: raise HTTPException(404, "Usuario no encontrado")
    return user_info

def fmt_price(val): return f"$ {val:,.0f}".replace(",", ".")

def get_full_image_url(path: str) -> str:
    if not path: return ""
    if path.startswith("http"): return path
    return f"{BASE_URL}/_upload/{path}"

# --- ENDPOINTS ---

# ... (Mantén get_cities, get_neighborhoods, login, register, forgot-password, get_products_for_mobile igual) ...
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
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path), category=p.category, description=p.content,
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
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path), category=p.category, description=p.content,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping
        ))
    return result

# --- ENDPOINT DE DETALLE CON OPINIONES BLINDADO ---
@router.get("/products/{product_id}", response_model=ProductDetailDTO)
async def get_product_detail(product_id: int, user_id: Optional[int] = None, session: Session = Depends(get_session)):
    try:
        # 1. Cargar producto
        p = session.get(BlogPostModel, product_id)
        if not p or not p.publish_active: 
            raise HTTPException(404, "Producto no encontrado")
        
        # 2. Cargar autor manualmente para evitar error de relación
        author_name = "Likemodas"
        seller_info_id = 0
        if p.userinfo_id:
            user_info_owner = session.get(UserInfo, p.userinfo_id)
            if user_info_owner:
                local_user_owner = session.get(LocalUser, user_info_owner.user_id)
                if local_user_owner:
                    author_name = local_user_owner.username
                seller_info_id = user_info_owner.id

        # 3. Imágenes y Variantes (Seguro)
        main_img = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        all_images_set = set()
        if main_img: all_images_set.add(main_img)
        if p.variants:
            for v in p.variants:
                for img in v.get("image_urls", []): all_images_set.add(img)
        
        final_images = [get_full_image_url(img) for img in all_images_set if img]
        main_image_final = get_full_image_url(main_img) if main_img else (final_images[0] if final_images else "")

        variants_dto = []
        if p.variants:
            for v in p.variants:
                v_img = v.get("image_urls", [])[0] if v.get("image_urls") else main_img
                v_images_list = [get_full_image_url(img) for img in v.get("image_urls", [])]
                if not v_images_list: v_images_list = [get_full_image_url(v_img)]

                variants_dto.append(VariantDTO(
                    id=v.get("variant_uuid", v.get("id", "")),
                    title=f"{v.get('attributes', {}).get('Color', '')} {v.get('attributes', {}).get('Talla', v.get('attributes', {}).get('Número', ''))}",
                    image_url=get_full_image_url(v_img),
                    price=v.get("price", p.price),
                    available_quantity=v.get("stock", 0),
                    images=v_images_list
                ))

        # 4. OPINIONES (NUEVO - SEGURO)
        reviews_list = []
        # Consultamos la tabla CommentModel directamente
        db_reviews = session.exec(select(CommentModel).where(CommentModel.blog_post_id == p.id)).all()
        
        ratings_sum = 0
        ratings_count = 0

        for r in db_reviews:
            try:
                ratings_sum += r.rating
                ratings_count += 1
                
                # Manejo seguro de fecha
                date_str = ""
                if r.created_at:
                    date_str = r.created_at.strftime("%d/%m/%Y")
                
                # Manejo seguro de nulos
                u_name = r.author_username if r.author_username else "Usuario"
                c_content = r.content if r.content else ""
                r_val = r.rating if r.rating is not None else 5

                reviews_list.append(ReviewDTO(
                    id=r.id,
                    username=u_name,
                    rating=int(r_val),
                    comment=c_content,
                    date=date_str
                ))
            except Exception as e:
                # Si una review falla, la saltamos pero no rompemos la app
                print(f"Error procesando review {r.id}: {e}")
                continue

        # Cálculo manual del promedio
        avg_rating = (ratings_sum / ratings_count) if ratings_count > 0 else 0.0

        # 5. Estado Usuario
        is_saved = False
        can_review = False
        if user_id and user_id > 0:
            user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
            if user_info:
                saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_info.id, SavedPostLink.blogpostmodel_id == p.id)).first()
                is_saved = saved is not None
                
                # Verificar compra
                has_bought = session.exec(select(PurchaseItemModel.id).join(PurchaseModel).where(PurchaseModel.userinfo_id == user_info.id, PurchaseItemModel.blogpostmodel_id == p.id)).first()
                
                # Verificar si ya opinó
                already_reviewed = any(r.userinfo_id == user_info.id for r in db_reviews)
                
                can_review = (has_bought is not None) and (not already_reviewed)

        date_created_str = ""
        if p.created_at:
            date_created_str = p.created_at.strftime("%d de %B del %Y")

        return ProductDetailDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            description=p.content, category=p.category,
            main_image_url=main_image_final, images=final_images, variants=variants_dto,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
            is_saved=is_saved, is_imported=p.is_imported, 
            
            average_rating=avg_rating, 
            rating_count=ratings_count,
            
            author=author_name, author_id=seller_info_id,
            created_at=date_created_str,
            reviews=reviews_list, 
            can_review=can_review
        )
    except Exception as e:
        print(f"ERROR CRITICO 500: {str(e)}")
        raise HTTPException(500, f"Error interno: {str(e)}")

# --- ENDPOINT PARA GUARDAR OPINIÓN ---
@router.post("/products/{product_id}/reviews")
async def create_product_review(product_id: int, body: ReviewSubmissionBody, session: Session = Depends(get_session)):
    try:
        user_info = get_user_info(session, body.user_id)
        
        # Verificar compra
        has_bought = session.exec(select(PurchaseItemModel).join(PurchaseModel).where(PurchaseModel.userinfo_id == user_info.id, PurchaseItemModel.blogpostmodel_id == product_id)).first()
        if not has_bought: raise HTTPException(400, "Debes comprar el producto para opinar.")
        
        # Verificar duplicados
        existing = session.exec(select(CommentModel).where(CommentModel.userinfo_id == user_info.id, CommentModel.blog_post_id == product_id)).first()
        if existing: raise HTTPException(400, "Ya has opinado sobre este producto.")
        
        username = "Usuario"
        initial = "U"
        if user_info.user:
            username = user_info.user.username
            initial = username[0].upper() if username else "U"

        new_review = CommentModel(
            userinfo_id=user_info.id,
            blog_post_id=product_id,
            rating=body.rating,
            content=body.comment, 
            author_username=username,
            author_initial=initial,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(new_review)
        session.commit()
        return {"message": "Opinión guardada"}
    except Exception as e:
        raise HTTPException(500, f"Error al guardar opinión: {str(e)}")

# ... (Resto de endpoints se mantienen) ...
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