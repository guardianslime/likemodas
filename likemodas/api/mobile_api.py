import os
import bcrypt
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import sqlalchemy
from sqlmodel import select, Session
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken, PurchaseModel, PurchaseItemModel, ShippingAddressModel

# --- AGREGAR AL INICIO CON LOS OTROS MODELOS ---
from likemodas.models import ShippingAddressModel
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping # Asegúrate de tener esto importado

from likemodas.services.email_service import send_verification_email, send_password_reset_email



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

class ProductMobileDTO(BaseModel):
    id: int
    title: str
    price: float
    price_formatted: str
    image_url: str
    category: str
    description: str
    is_available: bool
    combines_shipping: bool
    is_moda_completa: bool

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

# Nuevos DTOs para Seguridad y Direcciones
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class AddressDTO(BaseModel):
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str

# --- DTOs PARA CARRITO Y DIRECCIONES ---
class CartItemRequest(BaseModel):
    product_id: int
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
    address_id: Optional[int] = None # ID de la dirección usada para el cálculo

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

# --- ENDPOINTS ---

@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"El usuario no existe.")
        
        if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta.")

        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        
        if not user_info:
             raise HTTPException(status_code=400, detail="Perfil no encontrado")

        if not user_info.is_verified:
             raise HTTPException(status_code=403, detail="Cuenta no verificada.")

        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)

        return UserResponse(
            id=user_info.id,
            username=user.username,
            email=user_info.email,
            role=role_str,
            token=str(user.id)
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
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

        try:
            send_verification_email(recipient_email=creds.email, token=token_str)
        except Exception:
            pass 

        return UserResponse(id=new_info.id, username=new_user.username, email=new_info.email, role="customer", token=str(new_user.id))
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"Error registro: {str(e)}")

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
        try:
            send_password_reset_email(recipient_email=email, token=token_str)
        except Exception:
            pass
    return {"message": "OK"}

@router.get("/products", response_model=List[ProductMobileDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True)
    if category and category != "todos":
        query = query.where(BlogPostModel.category == category)
    query = query.order_by(BlogPostModel.created_at.desc())
    products = session.exec(query).all()
    result = []
    for p in products:
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        full_image_url = f"{BASE_URL}/_upload/{img_path}" if img_path else ""
        price_fmt = f"$ {p.price:,.0f}".replace(",", ".")
        
        result.append(ProductMobileDTO(
            id=p.id, 
            title=p.title, 
            price=p.price, 
            price_formatted=price_fmt, 
            image_url=full_image_url, 
            category=p.category, 
            description=p.content, 
            is_available=True,
            combines_shipping=p.combines_shipping,
            is_moda_completa=p.is_moda_completa_eligible
        ))
    return result

@router.get("/profile/{user_id}", response_model=ProfileDTO)
async def get_mobile_profile(user_id: int, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    local_user = session.get(LocalUser, user_id)
    avatar = f"{BASE_URL}/_upload/{user_info.avatar_url}" if user_info.avatar_url else ""

    return ProfileDTO(
        username=local_user.username if local_user else "Usuario",
        email=user_info.email,
        phone=user_info.phone or "",
        avatar_url=avatar
    )

@router.put("/profile/{user_id}")
async def update_mobile_profile(user_id: int, phone: str, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_info.phone = phone
    session.add(user_info)
    session.commit()
    return {"message": "Perfil actualizado"}

@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        return []

    purchases = session.exec(select(PurchaseModel).where(PurchaseModel.userinfo_id == user_info.id).order_by(PurchaseModel.purchase_date.desc())).all()

    history = []
    for p in purchases:
        items_dto = []
        for item in p.items:
            img = ""
            if item.blog_post and item.blog_post.variants:
                img_list = item.blog_post.variants[0].get("image_urls", [])
                if img_list:
                    img = f"{BASE_URL}/_upload/{img_list[0]}"
            items_dto.append(PurchaseItemDTO(title=item.blog_post.title if item.blog_post else "Producto", quantity=item.quantity, price=item.price_at_purchase, image_url=img))
        total_fmt = f"$ {p.total_price:,.0f}".replace(",", ".")
        history.append(PurchaseHistoryDTO(id=p.id, date=p.purchase_date.strftime('%d-%m-%Y'), status=p.status.value, total=total_fmt, items=items_dto))
    return history

# --- NUEVOS ENDPOINTS IMPLEMENTADOS ---

# 8. CAMBIAR CONTRASEÑA
@router.post("/profile/{user_id}/change-password")
async def change_password(user_id: int, req: ChangePasswordRequest, session: Session = Depends(get_session)):
    user = session.get(LocalUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not bcrypt.checkpw(req.current_password.encode('utf-8'), user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    
    new_hash = bcrypt.hashpw(req.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password_hash = new_hash
    session.add(user)
    session.commit()
    return {"message": "Contraseña actualizada"}

# 9. GUARDAR DIRECCIÓN
@router.post("/profile/{user_id}/address")
async def save_address(user_id: int, addr: AddressDTO, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si ya tiene direcciones, quitar el default de las anteriores
    existing = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).all()
    for a in existing:
        a.is_default = False
        session.add(a)
    
    new_addr = ShippingAddressModel(
        userinfo_id=user_info.id,
        name=addr.name,
        phone=addr.phone,
        city=addr.city,
        neighborhood=addr.neighborhood,
        address=addr.address,
        is_default=True
    )
    session.add(new_addr)
    session.commit()
    return {"message": "Dirección guardada"}

# 10. PUBLICACIONES GUARDADAS
@router.get("/profile/{user_id}/saved-posts", response_model=List[ProductMobileDTO])
async def get_saved_posts(user_id: int, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        return []
    
    # Cargar saved_posts (relación muchos a muchos)
    # Nota: Asumiendo que la relación está configurada en UserInfo como 'saved_posts'
    # Si Reflex no carga automáticamente, necesitarías una consulta join manual.
    # Aquí usamos la relación directa si el ORM lo permite.
    saved_posts = user_info.saved_posts 
    
    result = []
    for p in saved_posts:
        if not p.publish_active: continue
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        full_image_url = f"{BASE_URL}/_upload/{img_path}" if img_path else ""
        price_fmt = f"$ {p.price:,.0f}".replace(",", ".")
        result.append(ProductMobileDTO(
            id=p.id, title=p.title, price=p.price, price_formatted=price_fmt,
            image_url=full_image_url, category=p.category, description=p.content,
            is_available=True, combines_shipping=p.combines_shipping, is_moda_completa=p.is_moda_completa_eligible
        ))
    return result

# 1. OBTENER DIRECCIONES
@router.get("/addresses/{user_id}", response_model=List[AddressDTO])
async def get_addresses(user_id: int, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info: return []
    
    addresses = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id).order_by(ShippingAddressModel.is_default.desc())).all()
    return [AddressDTO(**addr.dict()) for addr in addresses]

# 2. CREAR DIRECCIÓN (Con lógica de predeterminada)
@router.post("/addresses/{user_id}")
async def create_address(user_id: int, req: CreateAddressRequest, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info: raise HTTPException(404, "Usuario no encontrado")

    # Si esta es la nueva predeterminada, quitar el flag a las otras
    if req.is_default:
        existing = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).all()
        for addr in existing:
            addr.is_default = False
            session.add(addr)
    
    # Si es la primera dirección, forzar que sea predeterminada
    count = session.exec(select(sqlalchemy.func.count()).select_from(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id)).one()
    is_def = req.is_default or (count == 0)

    new_addr = ShippingAddressModel(userinfo_id=user_info.id, **req.dict(exclude={'is_default'}), is_default=is_def)
    session.add(new_addr)
    session.commit()
    return {"message": "Dirección guardada"}

# 3. CALCULAR TOTALES DEL CARRITO (Simulando lógica web)
@router.post("/cart/calculate/{user_id}", response_model=CartSummaryResponse)
async def calculate_cart(user_id: int, req: CartCalculationRequest, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    
    # 1. Calcular Subtotal
    subtotal = 0.0
    for item in req.items:
        product = session.get(BlogPostModel, item.product_id)
        if product:
            subtotal += product.price * item.quantity
            
    # 2. Calcular Envío (Basado en dirección predeterminada)
    shipping_cost = 0.0
    address_id = None
    
    if user_info:
        default_addr = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == user_info.id, ShippingAddressModel.is_default == True)).first()
        
        if default_addr:
            address_id = default_addr.id
            # Aquí deberías llamar a tu lógica real de envíos (calculate_dynamic_shipping)
            # Por simplicidad para el ejemplo, si hay dirección cobramos 12.000, si es moda completa (subtotal > 200k) es gratis.
            # TÚ DEBES CONECTAR ESTO CON TU LÓGICA DE 'likemodas/logic/shipping_calculator.py'
            
            # Ejemplo simplificado:
            if subtotal >= 200000: # Umbral moda completa ejemplo
                shipping_cost = 0.0
            else:
                shipping_cost = 0.0 # O el valor base que tengas
                
            # NOTA: Para conectar con tu lógica real de Python, necesitarías importar y usar 
            # calculate_dynamic_shipping pasando los barrios del vendedor y comprador.
    
    total = subtotal + shipping_cost

    def fmt(val): return f"$ {val:,.0f}".replace(",", ".")

    return CartSummaryResponse(
        subtotal=subtotal, subtotal_formatted=fmt(subtotal),
        shipping=shipping_cost, shipping_formatted=fmt(shipping_cost),
        total=total, total_formatted=fmt(total),
        address_id=address_id
    )