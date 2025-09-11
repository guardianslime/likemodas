import os
import json
import sqlmodel
from fastapi import APIRouter, Request, Response, status, HTTPException
from datetime import datetime, timezone

# Importamos nuestro conector independiente
from likemodas.db.session import get_db_session
from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel

WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """
    Recibe el webhook de Wompi y actualiza la base de datos usando una sesión independiente.
    """
    raw_body = await request.body()
    
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")
    
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature.")
    
    try:
        event_data = json.loads(raw_body)
        transaction_data = event_data.get("data", {}).get("transaction", {})
        status = transaction_data.get("status")
        payment_link_id = transaction_data.get("payment_link_id")

        if status == "APPROVED" and payment_link_id:
            with get_db_session() as session:
                # 1. Buscar la compra
                purchase = session.exec(
                    sqlmodel.select(PurchaseModel).where(PurchaseModel.wompi_payment_link_id == payment_link_id)
                ).one_or_none()

                if purchase and purchase.status != PurchaseStatus.CONFIRMED:
                    # 2. Actualizar la compra
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    purchase.wompi_transaction_id = transaction_data.get("id")
                    session.add(purchase)
                    
                    # 3. (Opcional) Crear notificación
                    # Por ahora lo dejamos simple para asegurar que funcione.
                    # Podemos añadir notificaciones después.
                    
                    print(f"ÉXITO: Compra #{purchase.id} actualizada a CONFIRMED vía webhook independiente.")
                else:
                    print(f"Webhook ignorado: Compra no encontrada o ya confirmada.")
        else:
            print(f"Webhook ignorado: El estado no es 'APPROVED'.")

    except Exception as e:
        print(f"Error fatal en el webhook independiente: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    return Response(status_code=200)