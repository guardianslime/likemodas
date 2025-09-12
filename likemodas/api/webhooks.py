# likemodas/api/webhooks.py (Versión Corregida y Robusta)

import os
import json
import sqlmodel
import logging
from fastapi import APIRouter, Request, Response, HTTPException, status
from datetime import datetime, timezone

# Importaciones clave del proyecto
from likemodas.db.session import get_db_session
from likemodas.services.wompi_validator import verify_wompi_signature
from likemodas.models import PurchaseModel, PurchaseStatus

# Configuración del logger para este módulo específico
# Esto te dará logs mucho más informativos en Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET_ACTIVE")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/wompi")
async def handle_wompi_webhook(request: Request):
    """
    Recibe y procesa de forma segura los webhooks de Wompi, actualizando la BD
    con una sesión independiente y un manejo de errores robusto.
    """
    raw_body = await request.body()

    # Verificación de seguridad: ¿Está configurada la variable de entorno?
    if not WOMPI_EVENTS_SECRET:
        logger.error("CRÍTICO: La variable de entorno WOMPI_EVENTS_SECRET_ACTIVE no está configurada.")
        # Devolvemos un 500 para que el desarrollador vea el error de configuración en los logs.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured."
        )

    # Verificación de seguridad: ¿La firma es válida?
    if not verify_wompi_signature(raw_body, request.headers, WOMPI_EVENTS_SECRET):
        logger.warning("Intento de webhook con firma inválida recibido.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature."
        )

    # El bloque CRUCIAL que previene los errores 500
    try:
        event_data = json.loads(raw_body)
        transaction_data = event_data.get("data", {}).get("transaction", {})

        transaction_status = transaction_data.get("status")
        payment_link_id = transaction_data.get("payment_link_id")
        transaction_id = transaction_data.get("id")

        logger.info(f"Webhook de Wompi recibido. Link ID: {payment_link_id}, Status: {transaction_status}")

        if transaction_status == "APPROVED" and payment_link_id:
            # Usamos un gestor de contexto para asegurar que la sesión se cierre
            with get_db_session() as session:
                # 1. Buscar la compra usando el payment_link_id.
                purchase = session.exec(
                    sqlmodel.select(PurchaseModel).where(PurchaseModel.wompi_payment_link_id == payment_link_id)
                ).one_or_none()

                if purchase:
                    # 2. Verificar si la compra ya está confirmada (Idempotencia).
                    if purchase.status != PurchaseStatus.CONFIRMED:
                        # 3. Actualizar la compra.
                        purchase.status = PurchaseStatus.CONFIRMED
                        purchase.confirmed_at = datetime.now(timezone.utc)
                        purchase.wompi_transaction_id = transaction_id
                        session.add(purchase)
                        session.commit()
                        logger.info(f"ÉXITO: Compra #{purchase.id} actualizada a CONFIRMED vía webhook.")
                    else:
                        logger.info(f"Webhook ignorado (idempotencia): Compra #{purchase.id} ya estaba confirmada.")
                else:
                    logger.warning(f"Webhook recibido para un payment_link_id no encontrado en la BD: {payment_link_id}")
        else:
            logger.info(f"Webhook ignorado: El estado no es 'APPROVED' o falta payment_link_id. Estado recibido: {transaction_status}")

        # Si todo va bien, devolvemos un 200 OK para que Wompi sepa que todo está correcto.
        return Response(status_code=status.HTTP_200_OK, content='{"status": "event processed"}', media_type="application/json")

    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar el JSON del webhook de Wompi: {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content='{"error": "malformed request body"}', media_type="application/json")

    except Exception as e:
        # Este es el bloque que captura el error de la base de datos y cualquier otro.
        logger.error(f"Error fatal no capturado en el webhook de Wompi: {e}", exc_info=True)
        # Devolvemos un 500 para indicar a Wompi que hubo un problema y que debe reintentar el envío más tarde.
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='{"error": "internal server error processing webhook"}', media_type="application/json")