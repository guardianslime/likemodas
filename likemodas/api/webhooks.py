import os
import json
import reflex as rx
import sqlmodel
from fastapi import APIRouter, Request, Response, status, HTTPException
from datetime import datetime, timezone

from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.models import PurchaseModel, PurchaseStatus

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

def process_transaction_event_simplified(event: dict):
    """
    Versión simplificada que SOLO actualiza el estado de la compra.
    """
    transaction_data = event.get("data", {}).get("transaction", {})
    status = transaction_data.get("status")
    payment_link_id = transaction_data.get("payment_link_id")

    if status != "APPROVED" or not payment_link_id:
        print(f"Webhook (simplified) ignorado: status={status}, link_id={payment_link_id}")
        return

    print(f"Procesando webhook para payment_link_id: {payment_link_id}")
    with rx.session() as session:
        # 1. Buscar la compra (query simple, sin joins)
        purchase = session.exec(
            sqlmodel.select(PurchaseModel)
            .where(PurchaseModel.wompi_payment_link_id == payment_link_id)
        ).one_or_none()

        if not purchase:
            print(f"Compra con wompi_payment_link_id '{payment_link_id}' no encontrada.")
            return

        # 2. Actualizar solo los campos esenciales
        purchase.status = PurchaseStatus.CONFIRMED
        purchase.confirmed_at = datetime.now(timezone.utc)
        purchase.wompi_transaction_id = transaction_data.get("id")
        
        session.add(purchase)
        session.commit()
        print(f"¡ÉXITO! Compra #{purchase.id} actualizada a CONFIRMED.")

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """Endpoint que recibe el webhook y llama a la lógica simplificada."""
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        process_transaction_event_simplified(event_data)
    except Exception as e:
        print(f"Error al procesar el webhook (simplified): {e}")
        # Es crucial ver el traceback de este error en los logs de Railway
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    return Response(status_code=200)