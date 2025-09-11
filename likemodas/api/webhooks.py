import os
import json
import httpx
from fastapi import APIRouter, Request, Response, status, HTTPException
from reflex.config import get_config

from likemodas.services.wompi_validator import verify_wompi_signature

WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """
    Recibe el evento de Wompi, lo valida y lo reenvía al endpoint
    interno de Reflex para un procesamiento seguro.
    """
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        
        # Obtenemos la URL de nuestra propia API desde la configuración de Reflex
        config = get_config()
        # La URL del endpoint puente que creamos en likemodas.py
        bridge_endpoint_url = f"{config.api_url}/internal/process_wompi"

        # Hacemos una llamada interna a nuestro propio puente de Reflex
        async with httpx.AsyncClient() as client:
            # Aumentamos el timeout para estar seguros
            response = await client.post(bridge_endpoint_url, json=event_data, timeout=30.0)
            response.raise_for_status()

    except Exception as e:
        print(f"Error al reenviar evento al puente de Reflex: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    # Respondemos 200 OK a Wompi inmediatamente
    return Response(status_code=200)