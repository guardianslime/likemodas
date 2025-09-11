# likemodas/services/wompi_service.py (CORREGIDO)

import os
import httpx
from typing import Optional, Tuple

WOMPI_API_BASE_URL = os.getenv("WOMPI_API_BASE_URL", "https://sandbox.wompi.co/v1")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY_ACTIVE")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")

# --- ✨ FUNCIÓN MODIFICADA ✨ ---
async def create_wompi_payment_link(purchase_id: int, total_price: float) -> Optional[Tuple[str, str]]:
    """
    Crea un enlace de pago en Wompi.
    Devuelve una tupla con (checkout_url, payment_link_id) o None si falla.
    """
    if not WOMPI_PRIVATE_KEY:
        print("Error: La variable de entorno WOMPI_PRIVATE_KEY_ACTIVE no está configurada.")
        return None

    headers = {"Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"}
    
    payload = {
        "name": f"Compra #{purchase_id} en Likemodas",
        "description": f"Pago por productos de la compra #{purchase_id}",
        "single_use": True,
        "collect_shipping": False,
        "amount_in_cents": int(total_price * 100),
        "currency": "COP",
        "redirect_url": f"{APP_BASE_URL}/my-purchases",
        "reference": str(purchase_id), # Mantenemos la referencia original
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{WOMPI_API_BASE_URL}/payment_links", json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json().get("data", {})
            payment_link_id = response_data.get("id")
            
            if payment_link_id:
                checkout_url = f"https://checkout.wompi.co/l/{payment_link_id}"
                return checkout_url, payment_link_id  # Devolvemos ambos valores
            else:
                print(f"Error: No se encontró 'id' en la respuesta de Wompi: {response_data}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP al crear enlace de pago Wompi: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear enlace de pago Wompi: {e}")
            return None