# likemodas/services/wompi_service.py
import os
import httpx
from typing import Optional
from likemodas.models import PurchaseModel

# Lee las variables de entorno configuradas
WOMPI_API_BASE_URL = os.getenv("WOMPI_API_BASE_URL", "https://sandbox.wompi.co/v1")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY_ACTIVE")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")

async def create_wompi_payment_link(purchase: PurchaseModel) -> Optional[str]:
    """
    Crea un enlace de pago en Wompi para una compra específica[cite: 49].
    Devuelve la URL de checkout o None si falla.
    """
    if not WOMPI_PRIVATE_KEY:
        print("Error: La variable de entorno WOMPI_PRIVATE_KEY_ACTIVE no está configurada.")
        return None

    headers = {
        "Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"
    }
    
    # El payload se construye siguiendo la documentación de Wompi [cite: 51]
    payload = {
        "name": f"Compra #{purchase.id} en Likemodas",
        "single_use": True,
        "amount_in_cents": int(purchase.total_price * 100),
        "currency": "COP",
        "redirect_url": f"{APP_BASE_URL}/my-purchases", # Página de éxito/historial
        "reference": str(purchase.id), # ¡MUY IMPORTANTE! Asociamos nuestro ID de compra
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{WOMPI_API_BASE_URL}/payment_links", json=payload, headers=headers)
            response.raise_for_status()  # Lanza una excepción para errores HTTP
            
            response_data = response.json()
            payment_link_id = response_data.get("data", {}).get("id")
            
            if payment_link_id:
                return f"https://checkout.wompi.co/l/{payment_link_id}"
            else:
                print(f"Error: No se encontró 'id' en la respuesta de Wompi: {response_data}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP al crear enlace de pago Wompi: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear enlace de pago Wompi: {e}")
            return None