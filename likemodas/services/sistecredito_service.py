# likemodas/services/sistecredito_service.py

import os
import httpx
import asyncio
from typing import Optional, Dict, Any

# Cargar credenciales y URLs desde variables de entorno
SISTECREDITO_API_BASE_URL = os.getenv("SISTECREDITO_API_URL", "https://api.credinet.co")
SISTECREDITO_SUB_KEY = os.getenv("SISTECREDITO_SUB_KEY_PROD")
SISTECREDITO_APP_KEY = os.getenv("SISTECREDITO_STORE_ID")      # Mapeado a Storeid
SISTECREDITO_APP_TOKEN = os.getenv("SISTECREDITO_VENDOR_ID")    # Mapeado a Vendorid

def _get_auth_headers() -> Dict[str, str]:
    """Construye las cabeceras de autenticación reutilizables."""
    if not all([SISTECREDITO_SUB_KEY, SISTECREDITO_APP_KEY, SISTECREDITO_APP_TOKEN]):
        raise ValueError("Las credenciales de Sistecredito no están configuradas en las variables de entorno.")
    return {
        "Ocp-Apim-Subscription-Key": SISTECREDITO_SUB_KEY,
        "ApplicationKey": SISTECREDITO_APP_KEY,
        "ApplicationToken": SISTECREDITO_APP_TOKEN,
        "SCOrigen": "Production", # O "Staging" para pruebas
        "country": "CO",
        "Content-Type": "application/json"
    }

async def create_sistecredito_transaction(purchase_data: Dict[str, Any]) -> Optional[str]:
    """Inicia una transacción en Sistecredito y devuelve el ID para el sondeo."""
    headers = _get_auth_headers()
    endpoint = f"{SISTECREDITO_API_BASE_URL}/pay/create"

    # Construir el cuerpo de la solicitud dinámicamente
    body = {
        "invoice": str(purchase_data.get("purchase_id")),
        "description": f"Compra #{purchase_data.get('purchase_id')} en Likemodas",
        "paymentMethod": {"paymentMethodId": 2}, # ID para Sistecredito
        "currency": "COP",
        "value": int(purchase_data.get("total_price", 0)),
        "tax": int(purchase_data.get("tax", 0)),
        "taxBase": int(purchase_data.get("tax_base", 0)),
        "urlResponse": purchase_data.get("url_response"),
        "urlConfirmation": purchase_data.get("url_confirmation"),
        "methodConfirmation": "POST",
        "client": {
            "docType": "CC", # Asumir CC por ahora
            "document": purchase_data.get("client_document"),
            "name": purchase_data.get("client_name"),
            "lastName": purchase_data.get("client_lastname"),
            "email": purchase_data.get("client_email"),
            "indCountry": "57",
            "phone": purchase_data.get("client_phone"),
            "country": "CO",
            "city": purchase_data.get("shipping_city"),
            "address": purchase_data.get("shipping_address"),
            "ipAddress": purchase_data.get("ip_address", "0.0.0.0")
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(endpoint, json=body, headers=headers, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("errorCode") == 0 and response_data.get("data"):
                return response_data["data"].get("_id")
            else:
                print(f"Error en la respuesta de Sistecredito (create): {response_data.get('message')}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP al crear transacción Sistecredito: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear transacción Sistecredito: {e}")
            return None

async def poll_for_redirect_url(transaction_id: str, timeout: int = 45, delay: int = 3) -> Optional[str]:
    """Sondea el estado de una transacción hasta obtener la URL de redirección."""
    headers = _get_auth_headers()
    endpoint = f"{SISTECREDITO_API_BASE_URL}/pay/GetTransactionResponse"
    params = {"transactionId": transaction_id}
        
    async with httpx.AsyncClient() as client:
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                response = await client.get(endpoint, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                response_data = response.json().get("data", {})
                
                redirect_url = response_data.get("paymentMethodResponse", {}).get("paymentRedirectUrl")
                status = response_data.get("transactionStatus")

                if redirect_url:
                    return redirect_url
                
                if status in ["Approved", "Rejected", "Canceled", "Failed"]:
                    print(f"Sondeo terminado: Transacción {transaction_id} en estado final {status}.")
                    return None

                await asyncio.sleep(delay)
            except httpx.HTTPStatusError as e:
                print(f"Error HTTP durante el sondeo de Sistecredito: {e.response.status_code}")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Error inesperado durante el sondeo de Sistecredito: {e}")
                await asyncio.sleep(delay)
    
    print(f"Sondeo para la transacción {transaction_id} ha expirado (timeout).")
    return None

async def verify_transaction_status(transaction_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el estado verificado y completo de una transacción desde Sistecredito."""
    headers = _get_auth_headers()
    endpoint = f"{SISTECREDITO_API_BASE_URL}/pay/GetTransactionResponse"
    params = {"transactionId": transaction_id}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint, params=params, headers=headers, timeout=15.0)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("errorCode") == 0 and response_data.get("data"):
                return response_data["data"]
            else:
                print(f"Error en la respuesta de Sistecredito (verify): {response_data.get('message')}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP al verificar transacción en Sistecredito: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al verificar transacción en Sistecredito: {e}")
            return None