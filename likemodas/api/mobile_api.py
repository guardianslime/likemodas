import os
import bcrypt
import secrets
import logging # Para logs reales
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel

# Importamos la base de datos y modelos
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken
from likemodas.services.email_service import send_verification_email, send_password_reset_email

# Configuración de logs para verlos en Coolify
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# --- 1. LOGIN (A PRUEBA DE FALLOS) ---
@router.post("/login", response_model=UserResponse)
async def mobile_login(creds: LoginRequest, session: Session = Depends(get_session)):
    logger.info(f"--- Intento de login para: {creds.username} ---")
    
    try:
        # 1. Buscar usuario (LocalUser)
        user = session.exec(select(LocalUser).where(LocalUser.username == creds.username)).one_or_none()
        
        if not user:
            logger.warning("Usuario no encontrado en LocalUser")
            raise HTTPException(status_code=404, detail=f"El usuario '{creds.username}' no existe.")
        
        # 2. Diagnóstico de Contraseña
        try:
            # Convertimos a bytes explícitamente para evitar errores de tipo
            db_hash = bytes(user.password_hash)
            input_password = creds.password.encode('utf-8')
            
            # Verificación
            if not bcrypt.checkpw(input_password, db_hash):
                logger.warning("Password incorrecta")
                raise HTTPException(status_code=400, detail="Contraseña incorrecta.")
                
        except ValueError as ve:
            logger.error(f"Error de formato Hash: {ve}")
            raise HTTPException(status_code=400, detail=f"Error interno de Hash: {str(ve)}")
        except Exception as pe:
            logger.error(f"Error al verificar password: {pe}")
            raise HTTPException(status_code=400, detail=f"Error verificando password: {str(pe)}")

        # 3. Obtener perfil (UserInfo)
        user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
        
        if not user_info:
            logger.error(f"UserInfo no encontrado para user_id {user.id}")
            # Si falta UserInfo, lo creamos al vuelo para recuperar la cuenta (Autoreparación)
            try:
                logger.info("Intentando autoreparar UserInfo...")
                new_info = UserInfo(email=f"{creds.username}@recuperado.com", user_id=user.id, role=UserRole.CUSTOMER, is_verified=True)
                session.add(new_info)
                session.commit()
                session.refresh(new_info)
                user_info = new_info
            except Exception as e_rep:
                raise HTTPException(status_code=400, detail=f"Perfil corrupto y no se pudo reparar: {str(e_rep)}")

        # 4. Verificar email (Opcional: desactivar temporalmente si quieres probar acceso)
        if not user_info.is_verified:
            logger.warning("Usuario no verificado")
            raise HTTPException(status_code=403, detail="Cuenta no verificada. Revisa tu correo.")

        logger.info("Login exitoso")
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
        # CAPTURA CUALQUIER OTRO ERROR y lo envía al celular
        logger.error(f"ERROR FATAL NO CONTROLADO: {e}")
        # Devolvemos 400 en lugar de 500 para que la App muestre el mensaje
        raise HTTPException(status_code=400, detail=f"Error Fatal del Servidor: {str(e)}")

# ... (Mantén el resto de funciones register, forgot-password, products igual que antes) ...
# Copia y pega el resto de funciones (register, forgot-password, get_products) del código anterior aquí abajo.
# Asegúrate de que estén indentadas correctamente.

# --- 2. REGISTRO (Copia del código anterior) ---
@router.post("/register", response_model=UserResponse)
async def mobile_register(creds: RegisterRequest, session: Session = Depends(get_session)):
    # ... (Pega aquí el código de registro que te di en la respuesta anterior) ...
    # Si no lo tienes a mano, usa este simplificado:
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
        except Exception:
            pass
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
        img_path = p.main_image_url_variant or (p.variants[0]["image_urls"][0] if p.variants and p.variants[0].get("image_urls") else "")
        full_image_url = f"{BASE_URL}/_upload/{img_path}" if img_path else ""
        price_fmt = f"$ {p.price:,.0f}".replace(",", ".")
        result.append(ProductMobileDTO(id=p.id, title=p.title, price=p.price, price_formatted=price_fmt, image_url=full_image_url, category=p.category, description=p.content, is_available=True))
    return result