import os
import bcrypt
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel

# Importamos la base de datos y modelos
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken, PurchaseModel, PurchaseItemModel

from likemodas.services.email_service import send_verification_email, send_password_reset_email

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com" # Ajusta si es necesario en prod

# --- DTOs (Data Transfer Objects) ---

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

# --- ENDPOINTS ---

# 1. LOGIN
@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    logger.info(f"--- Intento de login para: {creds.username} ---")
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"El usuario '{creds.username}' no existe.")
        
        db_hash = bytes(user.password_hash)
        input_password = creds.password.encode('utf-8')
        
        if not bcrypt.checkpw(input_password, db_hash):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta.")

        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        
        if not user_info:
            # Autoreparación básica si falta UserInfo
            try:
                new_info = UserInfo(email=f"{creds.username}@recuperado.com", user_id=user.id, role=UserRole.CUSTOMER, is_verified=True)
                session.add(new_info)
                session.commit()
                session.refresh(new_info)
                user_info = new_info
            except Exception as e_rep:
                raise HTTPException(status_code=400, detail=f"Error de perfil: {str(e_rep)}")

        if not user_info.is_verified:
             raise HTTPException(status_code=403, detail="Cuenta no verificada. Revisa tu correo.")

        role_str = user_info.role.value if hasattr(user_info.role, 'value') else str(user_info.role)

        return UserResponse(
            id=user_info.id,
            username=user.username,
            email=user_info.email,
            role=role_str,
            token=str(user.id) # Usamos el ID como token simple para este ejemplo
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"ERROR FATAL: {e}")
        raise HTTPException(status_code=400, detail=f"Error Fatal: {str(e)}")

# 2. REGISTRO
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

# 3. RECUPERAR CONTRASEÑA
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

# 4. OBTENER PRODUCTOS
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

# 5. OBTENER PERFIL (NUEVO)
@router.get("/profile/{user_id}", response_model=ProfileDTO)
async def get_mobile_profile(user_id: int, session: Session = Depends(get_session)):
    # user_id aquí es el ID de LocalUser (que usamos como token)
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    local_user = session.get(LocalUser, user_id)
    
    avatar = ""
    if user_info.avatar_url:
        avatar = f"{BASE_URL}/_upload/{user_info.avatar_url}"

    return ProfileDTO(
        username=local_user.username if local_user else "Usuario",
        email=user_info.email,
        phone=user_info.phone or "",
        avatar_url=avatar
    )

# 6. ACTUALIZAR PERFIL (NUEVO)
@router.put("/profile/{user_id}")
async def update_mobile_profile(user_id: int, phone: str, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_info.phone = phone
    session.add(user_info)
    session.commit()
    return {"message": "Perfil actualizado"}

# 7. MIS COMPRAS (NUEVO)
@router.get("/purchases/{user_id}", response_model=List[PurchaseHistoryDTO])
async def get_mobile_purchases(user_id: int, session: Session = Depends(get_session)):
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).one_or_none()
    if not user_info:
        return []

    purchases = session.exec(
        select(PurchaseModel)
        .where(PurchaseModel.userinfo_id == user_info.id)
        .order_by(PurchaseModel.purchase_date.desc())
    ).all()

    history = []
    for p in purchases:
        items_dto = []
        for item in p.items:
            img = ""
            # Intentar obtener imagen
            if item.blog_post and item.blog_post.variants:
                # Intentar buscar la variante exacta si es posible, sino la primera
                img_list = item.blog_post.variants[0].get("image_urls", [])
                if img_list:
                    img = f"{BASE_URL}/_upload/{img_list[0]}"
            
            items_dto.append(PurchaseItemDTO(
                title=item.blog_post.title if item.blog_post else "Producto",
                quantity=item.quantity,
                price=item.price_at_purchase,
                image_url=img
            ))
            
        total_fmt = f"$ {p.total_price:,.0f}".replace(",", ".")

        history.append(PurchaseHistoryDTO(
            id=p.id,
            date=p.purchase_date.strftime('%d-%m-%Y'),
            status=p.status.value,
            total=total_fmt,
            items=items_dto
        ))
    
    return history