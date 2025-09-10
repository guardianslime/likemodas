# likemodas/api/webhooks.py
import os
import json
import sqlmodel
from fastapi import APIRouter, Request, Response, status, HTTPException
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.db.session import get_db_session
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel, PurchaseItemModel

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """Endpoint para recibir y procesar eventos de webhook de Wompi."""
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured.")
    
    # 1. Validar la firma criptográfica
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature.")
    
    # 2. Si la firma es válida, procesar el evento
    try:
        event_data = json.loads(raw_body)
        await process_transaction_event(event_data)
    except Exception as e:
        print(f"Error processing Wompi webhook: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    
    # 3. Responder a Wompi con un 200 OK para confirmar la recepción
    return Response(status_code=status.HTTP_200_OK)

async def process_transaction_event(event: dict):
    """Procesa un evento, actualiza la BD y notifica al comprador Y al vendedor."""
    transaction_data = event.get("data", {}).get("transaction", {})
    wompi_id = transaction_data.get("id")
    status = transaction_data.get("status")
    reference = transaction_data.get("reference")

    if not all([wompi_id, status, reference]):
        print("Webhook recibido sin datos de transacción esenciales.")
        return

    with get_db_session() as session:
        # Usamos opciones para cargar las relaciones que necesitaremos
        purchase = session.exec(
            sqlmodel.select(PurchaseModel)
            .options(selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post))
            .where(PurchaseModel.id == int(reference))
        ).one_or_none()

        if not purchase:
            print(f"Compra con referencia {reference} no encontrada.")
            return

        if purchase.status == PurchaseStatus.CONFIRMED:
            print(f"Compra {purchase.id} ya está confirmada. Ignorando evento.")
            return

        # Guardar datos de auditoría
        purchase.wompi_transaction_id = wompi_id
        if purchase.wompi_events is None:
            purchase.wompi_events = []
        purchase.wompi_events.append(event)
        
        if status == "APPROVED":
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            
            # 1. Notificación para el COMPRADOR
            buyer_notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado!",
                url="/my-purchases"
            )
            session.add(buyer_notification)

            # 2. Notificación para el VENDEDOR/VENDEDORES
            seller_ids = {item.blog_post.userinfo_id for item in purchase.items if item.blog_post}
            for seller_id in seller_ids:
                seller_notification = NotificationModel(
                    userinfo_id=seller_id,
                    message=f"¡Venta confirmada! Gestiona el envío para la orden #{purchase.id}.",
                    url="/admin/confirm-payments"
                )
                session.add(seller_notification)

        else: # DECLINED, ERROR, etc.
            purchase.status = PurchaseStatus.PENDING_PAYMENT
        
        session.add(purchase)