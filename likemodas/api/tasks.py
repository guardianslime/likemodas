import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone

from likemodas.db.session import get_session
from likemodas.models import PurchaseModel, PurchaseStatus, NotificationModel
from likemodas.services import wompi_service, sistecredito_service

router = APIRouter(prefix="/tasks", tags=["Cron Jobs"])

CRON_SECRET = os.getenv("CRON_SECRET")

@router.post("/reconcile-payments")
async def reconcile_pending_payments(secret: str, session: Session = Depends(get_session)):
    """
    [VERSIÓN FINAL] Cron job para reconciliar pagos pendientes tanto de Wompi
    como de Sistecredito.
    """
    if not CRON_SECRET or secret != CRON_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret.")

    wompi_updated_count = 0
    sistecredito_updated_count = 0

    # --- 1. Lógica de Reconciliación para Wompi (PENDING_PAYMENT) ---
    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    pending_wompi_purchases_stmt = select(PurchaseModel).where(
        PurchaseModel.status == PurchaseStatus.PENDING_PAYMENT,
        PurchaseModel.purchase_date < five_minutes_ago
    )
    pending_wompi_purchases = session.exec(pending_wompi_purchases_stmt).all()

    for purchase in pending_wompi_purchases:
        transaction = await wompi_service.get_transaction_by_reference(str(purchase.id))
        
        if transaction and transaction.get("status") == "APPROVED":
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            purchase.wompi_transaction_id = transaction.get("id")
            session.add(purchase)
            
            notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado!",
                url="/my-purchases"
            )
            session.add(notification)
            wompi_updated_count += 1

    # --- 2. Lógica de Reconciliación para Sistecredito (PENDING_SISTECREDITO_URL) ---
    ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
    stuck_sistecredito_purchases_stmt = select(PurchaseModel).where(
        PurchaseModel.status == PurchaseStatus.PENDING_SISTECREDITO_URL,
        PurchaseModel.purchase_date < ten_minutes_ago
    )
    stuck_sistecredito_purchases = session.exec(stuck_sistecredito_purchases_stmt).all()

    for purchase in stuck_sistecredito_purchases:
        if purchase.sistecredito_transaction_id:
            verified_data = await sistecredito_service.verify_transaction_status(purchase.sistecredito_transaction_id)
            if verified_data:
                status_final = verified_data.get("transactionStatus")
                
                if status_final == "Approved" and purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    purchase.sistecredito_authorization_code = verified_data.get("paymentMethodResponse", {}).get("authorizationCode")
                    purchase.sistecredito_invoice = verified_data.get("invoice")
                    session.add(purchase)
                    sistecredito_updated_count += 1
                
                elif status_final in ["Rejected", "Canceled", "Failed"] and purchase.status != PurchaseStatus.FAILED:
                    purchase.status = PurchaseStatus.FAILED
                    session.add(purchase)
                    sistecredito_updated_count += 1

    # --- 3. Guardar Cambios si hubo alguna actualización ---
    if wompi_updated_count > 0 or sistecredito_updated_count > 0:
        session.commit()

    return {
        "status": "success", 
        "wompi_reconciled": wompi_updated_count,
        "sistecredito_reconciled": sistecredito_updated_count
    }