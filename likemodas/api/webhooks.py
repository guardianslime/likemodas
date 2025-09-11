import os
import json
import reflex as rx
from fastapi import APIRouter, Request, Response, status, HTTPException

from likemodas.state import AppState
from likemodas.services.wompi_validator import verify_wompi_signature

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """
    Endpoint para recibir eventos de webhook de Wompi, validarlos,
    y delegar el procesamiento a una tarea en segundo plano de Reflex.
    """
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        
        # Obtenemos una instancia del estado de la aplicación
        state = await AppState.create()
        
        # Llamamos al EventHandler en segundo plano para procesar los datos
        await state.process_wompi_event_bg(event_data)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")
    except Exception as e:
        print(f"Error al delegar tarea de webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    # Respondemos a Wompi inmediatamente con 200 OK para que no reintente.
    # La tarea se ejecutará en segundo plano.
    return Response(status_code=200)