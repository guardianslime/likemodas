import os
import bcrypt
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import sqlalchemy
from sqlmodel import select, Session, col
from pydantic import BaseModel

from likemodas.db.session import get_session
# --- CORRECCIÓN 1: Importamos el nombre correcto del modelo ---
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken, PurchaseModel, PurchaseItemModel, ShippingAddressModel, SavedPostLink
from likemodas.services.email_service import send_verification_email, send_password_reset_email
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com" 

# --- DTOs (Sin cambios) ---
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
    description: str  # <--- AÑADE ESTA LÍNEA
    is_moda_completa: bool
    combines_shipping: bool

class VariantDTO(BaseModel):
    id: str
    title: str
    image_url: str
    price: float
    available_quantity: int

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

class CartSummaryResponse(BaseModel):
    subtotal: float
    subtotal_formatted: str
    shipping: float
    shipping_formatted: str
    total: float
    total_formatted: str
    address_id: Optional[int] = None

# --- HELPERS ---
def get_user_info(session: Session, user_id: int) -> UserInfo:
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info: raise HTTPException(404, "Usuario no encontrado")
    return user_info

def fmt_price(val): return f"$ {val:,.0f}".replace(",", ".")

def get_full_image_url(path: str) -> str:
    if not path: return ""
    return f"{BASE_URL}/_upload/{path}"

# --- ENDPOINTS ---

@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user: raise HTTPException(status_code=404, detail=f"El usuario no existe.")
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash): raise HTTPException(status_code=400, detail="Contraseña incorrecta.")
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        if not user_info: raise HTTPException(status_code=400, detail="Perfil no encontrado")
        if not user_info.is_verified: raise HTTPException(status_code=403, detail="Cuenta no verificada.")
        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)
        return UserResponse(id=user_info.id, username=user.username, email=user_info.email, role=role_str, token=str(user.id))
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first(): raise HTTPException(status_code=400, detail="El usuario ya existe")
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
        verification_token = VerificationToken(token=token_str, userinfo_id=new_info.id, expires_at=expires)
        session.add(verification_token)
        session.commit()
        try: send_verification_email(recipient_email=creds.email, token=token_str)
        except Exception: pass 
        return UserResponse(id=new_info.id, username=new_user.username, email=new_info.email, role="customer", token=str(new_user.id))
    except Exception as e: raise HTTPException(status_code=400, detail=f"Error registro: {str(e)}")

@router.post("/forgot-password")
async def mobile_forgot_password(req: ForgotPasswordRequest, session: Session = Depends(get_session)):
    email = req.email.strip().lower()
    user_info = session.exec(select(UserInfo).where(UserInfo.email == email)).one_or_none()
    if user_info:
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(token=token_str, user_id=user_info.user_id, expires_at=expires)
        session.add(reset_token)
        session.commit()
        try: send_password_reset_email(recipient_email=email, token=token_str)
        except Exception: pass
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
            image_url=get_full_image_url(img_path), category=p.category,
            description=p.content, # <--- AÑADE ESTA LÍNEA
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping
        ))
    return result

@router.get("/products/{product_id}", response_model=ProductDetailDTO)
async def get_product_detail(product_id: int, user_id: Optional[int] = None, session: Session = Depends(get_session)):
    p = session.get(BlogPostModel, product_id)
    if not p or not p.publish_active: raise HTTPException(404, "Producto no encontrado")
    
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
            variants_dto.append(VariantDTO(
                id=v.get("variant_uuid", v.get("id", "")), # Corrección UUID
                title=f"{v.get('attributes', {}).get('Color', '')} {v.get('attributes', {}).get('Talla', v.get('attributes', {}).get('Número', ''))}",
                image_url=get_full_image_url(v_img),
                price=v.get("price", p.price),
                available_quantity=v.get("stock", 0) # Corrección stock
            ))

    is_saved = False
    if user_id:
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
        if user_info:
            # --- CORRECCIÓN 2: Usamos SavedPostLink y blogpostmodel_id ---
            saved = session.exec(select(SavedPostLink).where(SavedPostLink.userinfo_id == user_info.id, SavedPostLink.blogpostmodel_id == p.id)).first()
            is_saved = saved is not None

    return ProductDetailDTO(
        id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
        description=p.content, category=p.category,
        main_image_url=main_image_final, images=final_images, variants=variants_dto,
        is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping,
        is_saved=is_saved
    )

@router.post("/products/{product_id}/toggle-save/{user_id}")
async def toggle_save_product(product_id: int, user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    product = session.get(BlogPostModel, product_id)
    if not product: raise HTTPException(404, "Producto no encontrado")

    # --- CORRECCIÓN 3: Usamos SavedPostLink y blogpostmodel_id ---
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

# ... (RESTO DEL CÓDIGO: PROFILE, ADDRESSES, PURCHASES, CART SE MANTIENEN IGUAL QUE EN LA VERSIÓN ANTERIOR)
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
    return [AddressDTO(**addr.dict()) for addr in addresses]

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
    new_addr = ShippingAddressModel(userinfo_id=user_info.id, **req.dict(exclude={'is_default'}), is_default=is_def)
    session.add(new_addr)
    session.commit()
    return {"message": "Dirección guardada"}

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
    saved_posts = user_info.saved_posts 
    result = []
    for p in saved_posts:
        if not p.publish_active: continue
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        result.append(ProductListDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=fmt_price(p.price),
            image_url=get_full_image_url(img_path), category=p.category,
            is_moda_completa=p.is_moda_completa_eligible, combines_shipping=p.combines_shipping
        ))
    return result

@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    purchases = session.exec(select(PurchaseModel).where(PurchaseModel.userinfo_id == user_info.id).order_by(PurchaseModel.purchase_date.desc())).all()
    history = []
    for p in purchases:
        items_dto = []
        for item in p.items:
            img = ""
            if item.blog_post:
                img_path = item.blog_post.main_image_url_variant or (item.blog_post.variants[0]["image_urls"][0] if item.blog_post.variants and item.blog_post.variants[0].get("image_urls") else "")
                img = get_full_image_url(img_path)
            items_dto.append(PurchaseItemDTO(title=item.blog_post.title if item.blog_post else "Producto", quantity=item.quantity, price=item.price_at_purchase, image_url=img))
        history.append(PurchaseHistoryDTO(id=p.id, date=p.purchase_date.strftime('%d-%m-%Y'), status=p.status.value, total=fmt_price(p.total_price), items=items_dto))
    return history

@router.post("/cart/calculate/{user_id}", response_model=CartSummaryResponse)
async def calculate_cart(user_id: int, req: CartCalculationRequest, session: Session = Depends(get_session)):
    user_info = get_user_info(session, user_id)
    subtotal = 0.0
    for item in req.items:
        product = session.get(BlogPostModel, item.product_id)
        if product:
            price = product.price
            if item.variant_id and product.variants:
                variant = next((v for v in product.variants if v.get("id") == item.variant_id), None)
                if variant: price = variant.get("price", product.price)
            subtotal += price * item.quantity
            
    shipping_cost = 0.0
    address_id = None
    default_addr = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id, ShippingAddressModel.is_default == True)).first()
    
    if default_addr:
        address_id = default_addr.id
        shipping_cost = 12000.0 # Fallback simplificado

    total = subtotal + shipping_cost
    return CartSummaryResponse(
        subtotal=subtotal, subtotal_formatted=fmt_price(subtotal),
        shipping=shipping_cost, shipping_formatted=fmt_price(shipping_cost),
        total=total, total_formatted=fmt_price(total), address_id=address_id
    )