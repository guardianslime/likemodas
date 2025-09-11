import os
import json
import httpx
import reflex as rx
from fastapi import APIRouter, Request, Response, status, HTTPException
from reflex.config import get_config

from likemodas.services.wompi_validator import verify_wompi_signature

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """
    Recibe el evento de Wompi, lo valida y lo reenvía a un endpoint
    interno de Reflex para un procesamiento seguro.
    """
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        
        # Obtenemos la URL de la API de nuestra configuración de Reflex
        config = get_config()
        api_url = f"{config.api_url}/wompi_event"

        # Usamos httpx para hacer una llamada interna al EventHandler de Reflex
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=event_data)
            response.raise_for_status() # Lanza un error si el EventHandler falla

    except Exception as e:
        print(f"Error al reenviar evento a la API de Reflex: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    # Respondemos a Wompi inmediatamente
    return Response(status_code=200)