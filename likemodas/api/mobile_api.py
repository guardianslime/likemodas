import os
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel

# Importamos la base de datos y modelos
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken
from likemodas.services.email_service import send_verification_email, send_password_reset_email

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

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile App"])
BASE_URL = "https://api.likemodas.com"

# --- 1. LOGIN (MODO DIAGNÓSTICO) ---
@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    try:
        # 1. Buscar usuario
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        
        if not user:
            # Si no encuentra el usuario, devolvemos 404
            raise HTTPException(status_code=404, detail=f"Usuario '{creds.username}' no existe en la BD")
        
        # 2. Verificar contraseña con seguridad extra
        try:
            # Aseguramos que el hash sea bytes, no memoryview
            hash_bytes = bytes(user.password_hash)
            input_bytes = creds.password.encode('utf-8')
            
            if not bcrypt.checkpw(input_bytes, hash_bytes):
                raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        except ValueError as ve:
            # Captura errores específicos de bcrypt (ej: salt inválido)
            raise HTTPException(status_code=400, detail=f"Error de formato de contraseña en BD: {str(ve)}")

        # 3. Obtener perfil
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Perfil de usuario (UserInfo) no encontrado")

        # 4. Verificar email
        if not user_info.is_verified:
            raise HTTPException(status_code=403, detail="Cuenta no verificada. Revisa tu email.")

        return UserResponse(
            id=user_info.id,
            username=user.username,
            email=user_info.email,
            role=user_info.role.value,
            token=str(user.id)
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        # ESTA ES LA CLAVE: En lugar de 500, devolvemos 400 con el mensaje del error real
        print(f"CRITICAL LOGIN ERROR: {e}")
        raise HTTPException(status_code=400, detail=f"DEBUG ERROR INTERNO: {str(e)}")

# --- 2. REGISTRO ---
@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(LocalUser).where(LocalUser.username == creds.username)).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    if session.exec(select(UserInfo).where(UserInfo.email == creds.email)).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

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

        # Intenta enviar correo, pero no falles todo el registro si el correo falla
        try:
            send_verification_email(recipient_email=creds.email, token=token_str)
        except Exception as e_mail:
            print(f"Error enviando email: {e_mail}")
            # No lanzamos error aquí para permitir que el usuario se cree, 
            # aunque tendrá que pedir reenvío de correo luego.

        return UserResponse(
            id=new_info.id,
            username=new_user.username,
            email=new_info.email,
            role="customer",
            token=str(new_user.id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

# --- 3. FORGOT PASSWORD ---
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
        except Exception as e:
            print(f"Error email: {e}")
    
    return {"message": "OK"}

# --- 4. PRODUCTOS ---
@router.get("/products", response_model=List[ProductMobileDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
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