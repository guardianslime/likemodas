# likemodas/services/wompi_service.py (CORREGIDO)

import os
import httpx
from typing import Optional
# Ya no necesitamos importar PurchaseModel aquí

# Las variables de entorno se mantienen igual
WOMPI_API_BASE_URL = os.getenv("WOMPI_API_BASE_URL", "https://sandbox.wompi.co/v1")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY_ACTIVE")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")

async def create_wompi_payment_link(purchase_id: int, total_price: float) -> Optional[str]:
    """
    Crea un enlace de pago en Wompi usando datos simples.
    Devuelve la URL de checkout o None si falla.
    """
    if not WOMPI_PRIVATE_KEY:
        print("Error: La variable de entorno WOMPI_PRIVATE_KEY_ACTIVE no está configurada.")
        return None

    headers = {
        "Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"
    }
    
    payload = {
        "name": f"Compra #{purchase_id} en Likemodas", # Usa purchase_id
        "single_use": True,
        "amount_in_cents": int(total_price * 100), # Usa total_price
        "currency": "COP",
        "redirect_url": f"{APP_BASE_URL}/my-purchases",
        "reference": str(purchase_id), # Usa purchase_id
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{WOMPI_API_BASE_URL}/payment_links", json=payload, headers=headers)
            response.raise_for_status()
            
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