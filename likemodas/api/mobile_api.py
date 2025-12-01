import os
import bcrypt
import secrets
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy
from sqlmodel import select, Session
from pydantic import BaseModel

from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, LocalUser, UserInfo, UserRole, VerificationToken, PasswordResetToken, PurchaseModel, PurchaseItemModel, ShippingAddressModel, SavedPostLink
from likemodas.services.email_service import send_verification_email, send_password_reset_email
# Importamos la lógica de envíos que ya usas en la web (Asegúrate de que este import funcione)
from likemodas.logic.shipping_calculator import calculate_dynamic_shipping

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
    average_rating: float
    rating_count: int

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
    if path.startswith("http"): return path
    return f"{BASE_URL}/_upload/{path}"

# --- ENDPOINTS ---
# (Login, Register, ForgotPassword, Products, Profile, Addresses... se mantienen igual)
# ... Copia los endpoints anteriores aquí si los borraste, o mantén los que ya tenías ...

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

# ... (Otros endpoints estándar omitidos para brevedad, asegúrate de tenerlos) ...
# Asegúrate de tener getProducts, getProductDetail, etc. tal cual estaban.

# --- AQUÍ ESTÁ LA MAGIA: EL ENDPOINT DE CÁLCULO REAL ---
@router.post("/cart/calculate/{user_id}", response_model=CartSummaryResponse)
async def calculate_cart(user_id: int, req: CartCalculationRequest, session: Session = Depends(get_session)):
    """
    Calcula el subtotal, envío dinámico y total del carrito usando la lógica real de negocio.
    """
    try:
        user_info = get_user_info(session, user_id)
        
        # 1. Obtener dirección predeterminada para cálculos de envío
        default_addr = session.exec(
            select(ShippingAddressModel)
            .where(ShippingAddressModel.userinfo_id == user_info.id, ShippingAddressModel.is_default == True)
        ).first()
        
        buyer_city = default_addr.city if default_addr else None
        buyer_barrio = default_addr.neighborhood if default_addr else None

        # 2. Cargar productos de la base de datos
        product_ids = [item.product_id for item in req.items]
        if not product_ids:
            return CartSummaryResponse(
                subtotal=0, subtotal_formatted="$ 0",
                shipping=0, shipping_formatted="$ 0",
                total=0, total_formatted="$ 0",
                address_id=default_addr.id if default_addr else None
            )

        db_posts = session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(product_ids))).all()
        post_map = {p.id: p for p in db_posts}

        # 3. Calcular Subtotal Base (Precio * Cantidad)
        subtotal_base = 0.0
        items_for_shipping = [] 
        
        for item in req.items:
            post = post_map.get(item.product_id)
            if post:
                # Usar precio base del post
                price = post.price
                subtotal_base += price * item.quantity
                items_for_shipping.append({"post": post, "quantity": item.quantity})

        # Calcular IVA (Asumimos que el precio ya lo incluye para simplificar visualización, igual que en web)
        subtotal_con_iva = subtotal_base 

        # 4. Lógica de Envío Gratis (Moda Completa)
        free_shipping_achieved = False
        moda_completa_items = [
            x["post"] for x in items_for_shipping 
            if x["post"].is_moda_completa_eligible
        ]
        
        if moda_completa_items:
            valid_thresholds = [p.free_shipping_threshold for p in moda_completa_items if p.free_shipping_threshold and p.free_shipping_threshold > 0]
            if valid_thresholds:
                highest_threshold = max(valid_thresholds)
                if subtotal_con_iva >= highest_threshold:
                    free_shipping_achieved = True

        # 5. Cálculo de Envío Dinámico
        final_shipping_cost = 0.0
        
        if not free_shipping_achieved and default_addr:
            # Agrupar productos por vendedor
            seller_groups = defaultdict(list)
            for x in items_for_shipping:
                post = x["post"]
                qty = x["quantity"]
                for _ in range(qty):
                    seller_groups[post.userinfo_id].append(post)

            # Obtener datos de ubicación de los vendedores
            seller_ids = list(seller_groups.keys())
            sellers_info = session.exec(select(UserInfo).where(UserInfo.id.in_(seller_ids))).all()
            seller_data_map = {info.id: {"city": info.seller_city, "barrio": info.seller_barrio} for info in sellers_info}

            for seller_id, items_from_seller in seller_groups.items():
                combinable_items = [p for p in items_from_seller if p.combines_shipping]
                individual_items = [p for p in items_from_seller if not p.combines_shipping]
                
                seller_data = seller_data_map.get(seller_id)
                seller_city = seller_data.get("city") if seller_data else None
                seller_barrio = seller_data.get("barrio") if seller_data else None

                # Costo para items individuales
                for individual_item in individual_items:
                    cost = calculate_dynamic_shipping(
                        base_cost=individual_item.shipping_cost or 0.0,
                        seller_barrio=seller_barrio,
                        buyer_barrio=buyer_barrio,
                        seller_city=seller_city,
                        buyer_city=buyer_city
                    )
                    final_shipping_cost += cost
                
                # Costo para items combinados
                if combinable_items:
                    valid_limits = [p.shipping_combination_limit for p in combinable_items if p.shipping_combination_limit and p.shipping_combination_limit > 0] or [1]
                    limit = min(valid_limits)
                    num_fees = math.ceil(len(combinable_items) / limit)
                    
                    highest_base_cost = max((p.shipping_cost or 0.0 for p in combinable_items), default=0.0)
                    
                    group_shipping_fee = calculate_dynamic_shipping(
                        base_cost=highest_base_cost,
                        seller_barrio=seller_barrio,
                        buyer_barrio=buyer_barrio,
                        seller_city=seller_city,
                        buyer_city=buyer_city
                    )
                    final_shipping_cost += (group_shipping_fee * num_fees)

        # 6. Total Final
        grand_total = subtotal_con_iva + final_shipping_cost

        return CartSummaryResponse(
            subtotal=subtotal_con_iva,
            subtotal_formatted=fmt_price(subtotal_con_iva),
            shipping=final_shipping_cost,
            shipping_formatted=fmt_price(final_shipping_cost),
            total=grand_total,
            total_formatted=fmt_price(grand_total),
            address_id=default_addr.id if default_addr else None
        )
    except Exception as e:
        print(f"Error calculando carrito: {e}")
        raise HTTPException(status_code=500, detail=str(e))