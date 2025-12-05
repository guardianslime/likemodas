import os
import httpx
from typing import Optional, Tuple

# Configuración de entorno
WOMPI_API_BASE_URL = os.getenv("WOMPI_API_BASE_URL", "https://sandbox.wompi.co/v1")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY_ACTIVE")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")

async def create_wompi_payment_link(purchase_id: int, total_price: float) -> Optional[Tuple[str, str]]:
    """
    Crea un enlace de pago en Wompi.
    """
    if not WOMPI_PRIVATE_KEY:
        print("Error: La variable de entorno WOMPI_PRIVATE_KEY_ACTIVE no está configurada.")
        return None

    headers = {"Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"}
    
    payload = {
        "name": f"Compra #{purchase_id} en Likemodas",
        "description": f"Pago por productos de la compra #{purchase_id}",
        "single_use": False, # Cambiado a False para permitir reintentos si el usuario falla la primera vez
        "collect_shipping": False,
        "amount_in_cents": int(total_price * 100),
        "currency": "COP",
        # URL a la que Wompi redirige al usuario al terminar
        "redirect_url": f"{APP_BASE_URL}/my-purchases", 
        "reference": str(purchase_id), 
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{WOMPI_API_BASE_URL}/payment_links", json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json().get("data", {})
            payment_link_id = response_data.get("id")
            
            if payment_link_id:
                # Construimos la URL web para el WebView
                checkout_url = f"https://checkout.wompi.co/l/{payment_link_id}"
                return checkout_url, payment_link_id
            else:
                print(f"Error: No se encontró 'id' en la respuesta de Wompi: {response_data}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP al crear enlace de pago Wompi: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear enlace de pago Wompi: {e}")
            return None
        
async def get_wompi_transaction_details(transaction_id: str) -> Optional[dict]:
    """Consulta los detalles de una transacción específica por su ID."""
    if not WOMPI_PRIVATE_KEY:
        return None

    headers = {"Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"}
    url = f"{WOMPI_API_BASE_URL}/transactions/{transaction_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("data")
        except Exception as e:
            print(f"Error consultando transacción Wompi {transaction_id}: {e}")
            return None
        
async def get_transaction_by_reference(reference: str) -> Optional[dict]:
    """
    [CORRECCIÓN CRÍTICA]
    Busca en TODAS las transacciones asociadas a una referencia (ID de compra).
    Devuelve la transacción APROBADA si existe.
    Si no hay aprobadas, devuelve la más reciente.
    """
    if not WOMPI_PRIVATE_KEY:
        return None

    headers = {"Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"}
    url = f"{WOMPI_API_BASE_URL}/transactions"
    params = {"reference": reference}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            transactions = response.json().get("data", [])
            
            if not transactions:
                return None
            
            # 1. Prioridad: Buscar si alguna fue APROBADA
            for tx in transactions:
                if tx.get("status") == "APPROVED":
                    return tx
            
            # 2. Si ninguna fue aprobada, devolvemos la primera de la lista (la más reciente)
            # para que el sistema vea el error (DECLINED, ERROR, etc)
            return transactions[0]

        except Exception as e:
            print(f"Error al buscar transacción por referencia {reference}: {e}")
            return None