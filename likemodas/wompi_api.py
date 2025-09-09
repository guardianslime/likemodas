# likemodas/wompi_api.py
import reflex as rx
import os
import hashlib
import hmac
from fastapi import Request, Response, status
from datetime import datetime, timezone
from sqlmodel import select
from .models import PurchaseModel, PurchaseStatus, UserInfo
from .wompi_client import wompi

@rx.api("/wompi/create-transaction")
async def create_transaction(request: Request):
    """
    Crea una transacción en Wompi a partir de un ID de compra.
    Obtiene los datos sensibles (monto, email) directamente desde la BD.
    """
    try:
        body = await request.json()
        purchase_id = body.get("purchase_id")
        
        with rx.session() as session:
            # Usamos selectinload para cargar eficientemente la relación con userinfo
            purchase = session.exec(
                select(PurchaseModel).options(rx.selectinload(PurchaseModel.userinfo)).where(PurchaseModel.id == purchase_id)
            ).first()
            
            if not purchase or not purchase.userinfo:
                return Response(content="Compra o usuario no encontrado", status_code=status.HTTP_404_NOT_FOUND)
            
            amount_in_cents = int(purchase.total_price * 100)
            customer_email = purchase.userinfo.email
            reference = f"likemodas-purchase-{purchase.id}-{int(datetime.now().timestamp())}"

        tx = wompi.create_transaction(
            amount_in_cents=amount_in_cents,
            currency="COP",
            customer_email=customer_email,
            reference=reference,
            redirect_url=os.getenv("WOMPI_REDIRECT_URL"),
        )

        wompi_tx_id = tx.get("data", {}).get("id")
        if not wompi_tx_id:
            raise Exception("Respuesta de Wompi inválida: no se recibió ID de transacción.")

        with rx.session() as session:
            purchase_to_update = session.get(PurchaseModel, purchase_id)
            if purchase_to_update:
                purchase_to_update.wompi_transaction_id = wompi_tx_id
                session.add(purchase_to_update)
                session.commit()
        
        return tx

    except Exception as e:
        print(f"ERROR: No se pudo crear la transacción en Wompi. Detalles: {e}")
        return Response(content="Error interno del servidor al procesar el pago.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@rx.api("/wompi/webhook")
async def wompi_webhook(request: Request):
    """
    Recibe y procesa notificaciones de Wompi.
    Implementa una validación de firma HMAC-SHA256 para seguridad.
    """
    try:
        body = await request.json()
        
        # --- VALIDACIÓN DE FIRMA ---
        wompi_events_secret = os.getenv("WOMPI_EVENTS_SECRET")
        if not wompi_events_secret:
            print("FATAL: WOMPI_EVENTS_SECRET no está configurado.")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        transaction_data = body.get("data", {}).get("transaction", {})
        signature_data = body.get("signature", {})
        timestamp = body.get("timestamp")
        
        properties = signature_data.get("properties", [])
        values_to_hash = []
        for prop in properties:
            keys = prop.split('.')
            value = transaction_data
            for key in keys:
                value = value.get(key) if isinstance(value, dict) else None
            values_to_hash.append(str(value))
        
        concatenated_string = "".join(values_to_hash) + str(timestamp) + wompi_events_secret
        calculated_hash = hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()
        provided_checksum = signature_data.get("checksum")

        if not hmac.compare_digest(calculated_hash, str(provided_checksum)):
            print(f"ALERTA DE SEGURIDAD: Firma de webhook inválida. Petición rechazada.")
            return Response(content="Firma inválida", status_code=status.HTTP_403_FORBIDDEN)
        
        # --- PROCESAMIENTO DEL EVENTO ---
        event_type = body.get("event")
        if event_type == "transaction.updated":
            transaction_id = transaction_data.get("id")
            status_wompi = transaction_data.get("status")
            
            with rx.session() as session:
                purchase = session.exec(
                    select(PurchaseModel).where(PurchaseModel.wompi_transaction_id == transaction_id)
                ).first()

                if purchase:
                    if not isinstance(purchase.wompi_events, list):
                        purchase.wompi_events = []
                    purchase.wompi_events.append(body)

                    if status_wompi == "APPROVED" and purchase.status != PurchaseStatus.CONFIRMED:
                        purchase.status = PurchaseStatus.PENDING_CONFIRMATION
                        purchase.confirmed_at = datetime.now(timezone.utc)
                    elif status_wompi in ["DECLINED", "VOIDED", "ERROR"]:
                        purchase.status = PurchaseStatus.PENDING_PAYMENT
                    
                    session.add(purchase)
                    session.commit()
        
        return {"ok": True}

    except Exception as e:
        print(f"ERROR: Falla al procesar el webhook de Wompi. Detalles: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)