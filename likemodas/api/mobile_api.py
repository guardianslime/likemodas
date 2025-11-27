# likemodas/api/mobile_api.py
import os
import bcrypt
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, Category, LocalUser, UserInfo, UserRole

# --- DTOs (Modelos de datos para recibir/enviar JSON) ---
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    token: str # En una app real usaríamos JWT, aquí usaremos el ID como token simple por ahora

class ProductMobileDTO(BaseModel):
    id: int
    title: str
    price: float
    price_formatted: str
    image_url: str
    category: str
    description: str
    is_available: bool

# --- Configuración Router ---
router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com"

# --- ENDPOINTS DE AUTENTICACIÓN ---

@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    # 1. Buscar usuario en LocalUser
    user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    # 2. Verificar contraseña (hash)
    if not bcrypt.checkpw(creds.password.encode('utf-8'), user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    # 3. Obtener info extra (Email, Rol)
    user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
    if not user_info:
        raise HTTPException(status_code=400, detail="Error en datos de perfil")

    return UserResponse(
        id=user_info.id,
        username=user.username,
        email=user_info.email,
        role=user_info.role.value,
        token=str(user.id) # Simple session ID por ahora
    )

@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    # 1. Validaciones básicas
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    if session.exec(select(UserInfo).where(UserInfo.email == creds.email)).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # 2. Crear LocalUser
    hashed_pw = bcrypt.hashpw(creds.password.encode('utf-8'), bcrypt.gensalt())
    new_user = LocalUser(username=creds.username, password_hash=hashed_pw, enabled=True)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # 3. Crear UserInfo
    new_info = UserInfo(email=creds.email, user_id=new_user.id, role=UserRole.CUSTOMER)
    session.add(new_info)
    session.commit()
    session.refresh(new_info)

    return UserResponse(
        id=new_info.id,
        username=new_user.username,
        email=new_info.email,
        role="customer",
        token=str(new_user.id)
    )

# --- TUS ENDPOINTS DE PRODUCTOS (Mantenlos) ---
@router.get("/products", response_model=List[ProductMobileDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
    # ... (Tu código anterior de productos va aquí igual) ...
    # Copia el contenido de la función get_products_for_mobile que ya funcionaba
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True)
    if category and category != "todos":
        query = query.where(BlogPostModel.category == category)
    query = query.order_by(BlogPostModel.created_at.desc())
    products = session.exec(query).all()
    
    result = []
    for p in products:
        img_path = ""
        if p.main_image_url_variant:
            img_path = p.main_image_url_variant
        elif p.variants and len(p.variants) > 0 and p.variants[0].get("image_urls"):
            img_path = p.variants[0]["image_urls"][0]
            
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
            is_available=True
        ))
    return result