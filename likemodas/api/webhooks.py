import os
import json
import reflex as rx
import sqlmodel
from fastapi import APIRouter, Request, Response, status, HTTPException
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from likemodas.services.wompi_validator import verify_wompi_signature
# Se elimina la importación de get_db_session
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel, PurchaseItemModel

# Carga el secreto desde las variables de entorno
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

def process_transaction_event_sync(event: dict):
    """
    Procesa un evento de forma síncrona usando la sesión de base de datos de Reflex.
    """
    transaction_data = event.get("data", {}).get("transaction", {})
    wompi_id = transaction_data.get("id")
    status = transaction_data.get("status")
    payment_link_id = transaction_data.get("payment_link_id")

    if not all([wompi_id, status, payment_link_id]):
        print(f"Webhook (sync) recibido sin datos esenciales. Faltó 'payment_link_id'.")
        return

    # Usamos la sesión oficial de Reflex para garantizar la consistencia.
    with rx.session() as session:
        purchase = session.exec(
            sqlmodel.select(PurchaseModel)
            .options(selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post))
            .where(PurchaseModel.wompi_payment_link_id == payment_link_id)
        ).one_or_none()

        if not purchase:
            print(f"Compra con wompi_payment_link_id '{payment_link_id}' no encontrada.")
            return

        if purchase.status == PurchaseStatus.CONFIRMED:
            print(f"Compra {purchase.id} ya está confirmada. Ignorando evento.")
            return

        purchase.wompi_transaction_id = wompi_id
        if purchase.wompi_events is None:
            purchase.wompi_events = []
        purchase.wompi_events.append(event)
        
        if status == "APPROVED":
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            
            buyer_notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado!",
                url="/my-purchases"
            )
            session.add(buyer_notification)

            seller_ids = {item.blog_post.userinfo_id for item in purchase.items if item.blog_post}
            for seller_id in seller_ids:
                seller_notification = NotificationModel(
                    userinfo_id=seller_id,
                    message=f"¡Venta confirmada! Gestiona el envío para la orden #{purchase.id}.",
                    url="/admin/confirm-payments"
                )
                session.add(seller_notification)
        else:
            purchase.status = PurchaseStatus.PENDING_PAYMENT
        
        session.add(purchase)
        session.commit()
        print(f"Webhook (sync) procesado: Compra #{purchase.id} actualizada a {purchase.status.value}")

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """Endpoint para recibir y procesar eventos de webhook de Wompi."""
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        # Llamamos a la nueva función síncrona
        process_transaction_event_sync(event_data)
    except Exception as e:
        print(f"Error al procesar el webhook de Wompi: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    return Response(status_code=200)