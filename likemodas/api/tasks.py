# likemodas/api/tasks.py
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone

from likemodas.db.session import get_session
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel
from likemodas.services import wompi_service

router = APIRouter(prefix="/tasks", tags=["Cron Jobs"])

CRON_SECRET = os.getenv("CRON_SECRET")

@router.post("/reconcile-payments")
async def reconcile_pending_payments(secret: str, session: Session = Depends(get_session)):
    if not CRON_SECRET or secret != CRON_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret.")

    # Busca compras pendientes de pago de más de 5 minutos de antigüedad
    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    pending_purchases_stmt = select(PurchaseModel).where(
        PurchaseModel.status == PurchaseStatus.PENDING_PAYMENT,
        PurchaseModel.purchase_date < five_minutes_ago
    )
    pending_purchases = session.exec(pending_purchases_stmt).all()

    if not pending_purchases:
        return {"status": "success", "message": "No pending purchases to reconcile."}

    updated_count = 0
    for purchase in pending_purchases:
        # Busca la transacción en Wompi usando el ID de la compra como referencia
        transaction = await wompi_service.get_transaction_by_reference(str(purchase.id))
        
        if transaction and transaction.get("status") == "APPROVED":
            # Si se encontró y está aprobada, actualizamos nuestra base de datos
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            purchase.wompi_transaction_id = transaction.get("id")
            session.add(purchase)
            
            # Notificar al usuario que su pago fue confirmado
            notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado! Ya puedes ver los detalles en tu historial.",
                url="/my-purchases"
            )
            session.add(notification)
            
            updated_count += 1
    
    if updated_count > 0:
        session.commit()

    return {"status": "success", "reconciled_count": updated_count}