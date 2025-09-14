# likemodas/api/webhooks.py (Versión Final con Inyección de Dependencias)

import os
import json
import sqlmodel
import logging
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends  # <-- 1. IMPORTAR Depends
from sqlmodel import Session  # <-- 2. IMPORTAR Session
from datetime import datetime, timezone

# 3. IMPORTAR LA NUEVA FUNCIÓN DE SESIÓN
from likemodas.db.session import get_session
from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.services import sistecredito_service # ✨ AÑADE ESTE IMPORT
from likemodas.models import PurchaseModel, PurchaseStatus

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
# --- 4. MODIFICACIÓN CRÍTICA EN LA FIRMA DE LA FUNCIÓN ---
async def handle_wompi_webhook(request: Request, session: Session = Depends(get_session)):
    """
    Recibe y procesa de forma segura los webhooks de Wompi, usando una sesión de BD
    inyectada por FastAPI para máxima robustez.
    """
    raw_body = await request.body()

    if not WOMPI_EVENTS_SECRET:
        logger.error("CRÍTICO: La variable de entorno WOMPI_EVENTS_SECRET_ACTIVE no está configurada.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured.")

    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        logger.warning("Intento de webhook con firma inválida recibido.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature.")

    try:
        event_data = json.loads(raw_body)
        transaction_data = event_data.get("data", {}).get("transaction", {})
        
        transaction_status = transaction_data.get("status")
        payment_link_id = transaction_data.get("payment_link_id")
        transaction_id = transaction_data.get("id")

        logger.info(f"Webhook de Wompi recibido. Link ID: {payment_link_id}, Status: {transaction_status}")

        if transaction_status == "APPROVED" and payment_link_id:
            # --- 5. LÓGICA SIMPLIFICADA: Ya no necesitamos el 'with' ---
            # La variable 'session' es la sesión fresca y lista para usar que nos dio FastAPI.
            purchase = session.exec(
                sqlmodel.select(PurchaseModel).where(PurchaseModel.wompi_payment_link_id == payment_link_id)
            ).one_or_none()

            if purchase:
                if purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    purchase.wompi_transaction_id = transaction_id
                    session.add(purchase)
                    # El session.commit() se hará automáticamente al final por el generador `get_session`
                    logger.info(f"ÉXITO: Compra #{purchase.id} actualizada a CONFIRMED vía webhook.")
                else:
                    logger.info(f"Webhook ignorado (idempotencia): Compra #{purchase.id} ya estaba confirmada.")
            else:
                logger.warning(f"Webhook recibido para un payment_link_id no encontrado en la BD: {payment_link_id}")
        else:
            logger.info(f"Webhook ignorado: El estado no es 'APPROVED' o falta payment_link_id. Estado recibido: {transaction_status}")

        return Response(status_code=status.HTTP_200_OK, content='{"status": "event processed"}', media_type="application/json")

    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar el JSON del webhook de Wompi: {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content='{"error": "malformed request body"}', media_type="application/json")
    
    except Exception as e:
        logger.error(f"Error fatal no capturado en el webhook de Wompi: {e}", exc_info=True)
        # Devolver un 500 para indicar a Wompi que hubo un problema.
        # El session.rollback() se hará automáticamente por el generador `get_session`.
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='{"error": "internal server error processing webhook"}', media_type="application/json")
    

# --- ✨ AÑADE ESTE NUEVO ENDPOINT COMPLETO ---
@router.post("/sistecredito")
async def handle_sistecredito_webhook(request: Request, session: Session = Depends(get_session)):
    """Recibe y procesa de forma segura los webhooks de Sistecredito."""
    try:
        payload = await request.json()
        transaction_id = payload.get("_id")

        if not transaction_id:
            logger.warning("Webhook de Sistecredito recibido sin _id.")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        # Verificación por Callback - La única fuente de verdad
        verified_data = await sistecredito_service.verify_transaction_status(transaction_id)
        if not verified_data:
            logger.error(f"No se pudo verificar la transacción {transaction_id} de Sistecredito.")
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        status_final = verified_data.get("transactionStatus")
        
        purchase = session.exec(
            sqlmodel.select(PurchaseModel).where(PurchaseModel.sistecredito_transaction_id == transaction_id)
        ).one_or_none()

        if not purchase:
            logger.warning(f"Webhook recibido para transacción Sistecredito no encontrada en BD: {transaction_id}")
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        if status_final == "Approved" and purchase.status != PurchaseStatus.CONFIRMED:
            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.now(timezone.utc)
            purchase.sistecredito_authorization_code = verified_data.get("paymentMethodResponse", {}).get("authorizationCode")
            purchase.sistecredito_invoice = verified_data.get("invoice")
            session.add(purchase)
            session.commit()
            logger.info(f"ÉXITO: Compra #{purchase.id} (Sistecredito) actualizada a CONFIRMED vía webhook.")
        
        elif status_final in ["Rejected", "Canceled", "Failed"] and purchase.status != PurchaseStatus.FAILED:
            purchase.status = PurchaseStatus.FAILED
            session.add(purchase)
            session.commit()
            logger.info(f"Compra #{purchase.id} (Sistecredito) marcada como FAILED vía webhook.")
            
        return Response(status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fatal en webhook de Sistecredito: {e}", exc_info=True)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
