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
    print(f"--- INTENTO DE LOGIN MÓVIL ---")
    print(f"Usuario recibido: '{creds.username}'")
    # Imprimimos la longitud y los primeros/últimos caracteres para no revelar la password completa en logs
    print(f"Password recibida (longitud): {len(creds.password)}")
    print(f"Password recibida (bytes): {creds.password.encode('utf-8')}")
    
    try:
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        
        if not user:
            print(f"FALLO: Usuario '{creds.username}' no encontrado en BD.")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        print(f"Usuario encontrado en BD. ID: {user.id}")
        print(f"Hash en BD (bytes): {user.password_hash}")

        # Intento de verificación
        input_bytes = creds.password.encode('utf-8')
        hash_bytes = bytes(user.password_hash)
        
        if bcrypt.checkpw(input_bytes, hash_bytes):
            print("¡CONTRASEÑA CORRECTA!")
        else:
            print("FALLO: bcrypt.checkpw devolvió False.")
            # Prueba extra: Verificar si hay espacios en blanco
            if bcrypt.checkpw(creds.password.strip().encode('utf-8'), hash_bytes):
                print("AVISO: La contraseña funcionó al hacerle .strip(). El cliente envía espacios extra.")

            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        
        if not user_info:
             raise HTTPException(status_code=400, detail="Perfil corrupto")

        if not user_info.is_verified:
            raise HTTPException(status_code=403, detail="Cuenta no verificada")

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
        print(f"ERROR CRÍTICO: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

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