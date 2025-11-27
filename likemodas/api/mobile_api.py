# likemodas/api/mobile_api.py
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from pydantic import BaseModel

# Importamos tus modelos y sesión existentes
from likemodas.db.session import get_session
from likemodas.models import BlogPostModel, Category

# URL base de tu servidor (cámbiala por tu dominio real en producción)
# Forzamos la URL correcta para evitar errores de configuración
BASE_URL = "https://api.likemodas.com"

# 1. Definimos el "DTO" (Cómo se verán los datos en el celular)
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

# 2. El Endpoint: La app llamará a esta dirección
@router.get("/products", response_model=List[ProductMobileDTO])
async def get_products_for_mobile(category: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Devuelve los productos en formato JSON para Android.
    """
    # Consulta a tu base de datos existente
    query = select(BlogPostModel).where(BlogPostModel.publish_active == True)
    
    if category and category != "todos":
        query = query.where(BlogPostModel.category == category)
    
    # Ordenar por más recientes (igual que tu web)
    query = query.order_by(BlogPostModel.created_at.desc())
    products = session.exec(query).all()
    
    result = []
    for p in products:
        # Lógica para obtener la imagen principal (tomada de tu state.py)
        img_path = ""
        if p.main_image_url_variant:
            img_path = p.main_image_url_variant
        elif p.variants and len(p.variants) > 0 and p.variants[0].get("image_urls"):
            img_path = p.variants[0]["image_urls"][0]
            
        # Construimos la URL completa para que el celular la pueda descargar
        full_image_url = f"{BASE_URL}/_upload/{img_path}" if img_path else ""

        # Formatear precio (simulado, ya que tu función format_to_cop es de frontend)
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