# likemodas/api/webhooks.py
import os
import json
from fastapi import APIRouter, Request, Response, status, HTTPException
from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.db.session import get_db_session
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel
from datetime import datetime, timezone

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """Endpoint para recibir y procesar eventos de webhook de Wompi."""
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured.")
    
    # 1. Validar la firma criptográfica ANTES de procesar nada [cite: 144]
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature.")
    
    # 2. Si la firma es válida, procesar el evento
    try:
        event_data = json.loads(raw_body)
        await process_transaction_event(event_data)
    except Exception as e:
        print(f"Error processing Wompi webhook: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    
    # 3. Responder a Wompi con un 200 OK para confirmar la recepción [cite: 39]
    return Response(status_code=status.HTTP_200_OK)

async def process_transaction_event(event: dict):
    """Procesa un evento de transacción validado y actualiza la base de datos."""
    transaction_data = event.get("data", {}).get("transaction", {})
    wompi_id = transaction_data.get("id")
    status = transaction_data.get("status")
    reference = transaction_data.get("reference") # Nuestro ID de compra [cite: 154]

    if not all([wompi_id, status, reference]):
        print("Webhook recibido sin datos de transacción esenciales.")
        return

    with get_db_session() as session:
        purchase = session.get(PurchaseModel, int(reference))
        if not purchase:
            print(f"Compra con referencia {reference} no encontrada.")
            return

        # Manejo de Idempotencia: si ya está confirmada, no hacer nada [cite: 179]
        if purchase.status == PurchaseStatus.CONFIRMED:
            print(f"Compra {purchase.id} ya está confirmada. Ignorando evento duplicado.")
            return

        # Guardar datos de auditoría
        purchase.wompi_transaction_id = wompi_id
        if purchase.wompi_events is None:
            purchase.wompi_events = []
        purchase.wompi_events.append(event)
        
        # Actualizar estado basado en el evento
        if status == "APPROVED":
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            
            # Crear una notificación para el usuario [cite: 174]
            notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado!",
                url="/my-purchases"
            )
            session.add(notification)
        else: # DECLINED, ERROR, etc.
            purchase.status = PurchaseStatus.PENDING_PAYMENT # O un estado FAILED
        
        session.add(purchase)