# likemodas/api/tasks.py
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone

from likemodas.db.session import get_session
from likemodas.models import PurchaseModel, PurchaseStatus
from likemodas.services import wompi_service

router = APIRouter(prefix="/tasks", tags=["Cron Jobs"])

# Una "contraseña" simple para proteger el endpoint. Pon un valor largo y secreto en tus variables de entorno.
CRON_SECRET = os.getenv("CRON_SECRET") 

@router.post("/reconcile-payments")
async def reconcile_pending_payments(secret: str, session: Session = Depends(get_session)):
    if not CRON_SECRET or secret != CRON_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret.")

    ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)

    pending_purchases = session.exec(
        select(PurchaseModel).where(
            PurchaseModel.status == PurchaseStatus.PENDING_PAYMENT,
            PurchaseModel.purchase_date < ten_minutes_ago,
            PurchaseModel.wompi_payment_link_id != None # Solo las que tienen link de wompi
        )
    ).all()

    if not pending_purchases:
        return {"status": "success", "message": "No pending purchases to reconcile."}

    updated_count = 0
    for purchase in pending_purchases:
        # Asumimos que el ID del link de pago puede ser usado para encontrar la transacción.
        # NOTA: Wompi no permite buscar por link_id, esto es una limitación. La mejor referencia es el ID de transacción si lo tuviéramos.
        # Por ahora, este es un placeholder de la lógica que necesitarías.
        # La referencia es la forma correcta de reconciliar.

        # La lógica real debería consultar transacciones por referencia, pero la API de Wompi no lo facilita.
        # Este es un punto débil, pero es el mejor esfuerzo sin webhooks.
        pass # Aquí iría la lógica de consulta si la API de Wompi lo permitiera fácilmente.

    return {"status": "success", "reconciled_count": updated_count}