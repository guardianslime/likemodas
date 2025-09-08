# likemodas/api/wompi_api.py

import os
import httpx
import reflex as rx
import hashlib

import sqlalchemy
from fastapi import Request
from sqlmodel import select
from datetime import datetime, timezone

from ..models import PurchaseModel, PurchaseStatus, BlogPostModel, PurchaseItemModel
from ..state import AppState

# --- Variables de Entorno de Wompi ---
WOMPI_API_URL = "https://sandbox.wompi.co/v1"
WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY")
WOMPI_INTEGRITY_SECRET = os.getenv("WOMPI_INTEGRITY_SECRET")

@rx.api(route="/wompi/create_checkout_session")
async def create_wompi_checkout(request: Request) -> dict:
    """
    Endpoint que recibe los datos de la compra, crea la sesión en Wompi y devuelve una URL de pago.
    """
    try:
        body = await request.json()
        purchase_id = body.get("purchase_id")
        amount_cop = body.get("amount")
        customer_email = body.get("customer_email")
        redirect_url = body.get("redirect_url")

        if not all([purchase_id, amount_cop, customer_email, redirect_url]):
            return {"error": "Faltan datos requeridos."}, 400

        amount_in_cents = int(float(amount_cop) * 100)
        reference = f"likemodas-purchase-{purchase_id}"
        
        # Calcular la firma de integridad
        concatenation = f"{reference}{amount_in_cents}COP{WOMPI_INTEGRITY_SECRET}"
        signature = hashlib.sha256(concatenation.encode("utf-8")).hexdigest()

        # Datos para enviar a Wompi
        wompi_payload = {
            "currency": "COP",
            "amount_in_cents": amount_in_cents,
            "reference": reference,
            "signature:integrity": signature,
            "customer_email": customer_email,
            "redirect_url": redirect_url,
        }

        # La petición a Wompi para crear el "payment link"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WOMPI_API_URL}/checkouts",
                headers={"Authorization": f"Bearer {WOMPI_PUBLIC_KEY}"},
                json=wompi_payload
            )
            response.raise_for_status()
            wompi_data = response.json()
            
            # Devolvemos el ID de la sesión de Wompi para redirigir
            return {"checkout_id": wompi_data.get("data", {}).get("id")}

    except httpx.HTTPStatusError as e:
        print(f"Error de Wompi: {e.response.text}")
        return {"error": "Error al comunicarse con Wompi."}, 500
    except Exception as e:
        print(f"Error interno: {e}")
        return {"error": "Error interno del servidor."}, 500

@rx.api(route="/wompi/webhook")
async def wompi_webhook(request: Request) -> dict:
    """
    Endpoint para recibir las notificaciones de Wompi sobre el estado del pago.
    """
    try:
        payload = await request.json()
        print(f"Webhook de Wompi recibido: {payload}")

        transaction_data = payload.get("data", {}).get("transaction", {})
        status = transaction_data.get("status")
        reference = transaction_data.get("reference")

        if not reference or not reference.startswith("likemodas-purchase-"):
            return {"status": "ok", "message": "Ignorando referencia no válida"}

        purchase_id = int(reference.split("-")[-1])

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if not purchase:
                print(f"Error: Compra con ID {purchase_id} no encontrada.")
                return {"error": "Compra no encontrada"}, 404

            if status == "APPROVED" and purchase.status != PurchaseStatus.CONFIRMED:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                session.add(purchase)

                # Deducir stock
                for item in purchase.items:
                    post = session.get(BlogPostModel, item.blog_post_id)
                    if post:
                        variant_updated = False
                        for variant in post.variants:
                            if variant.get("attributes") == item.selected_variant:
                                variant["stock"] = variant.get("stock", 0) - item.quantity
                                variant_updated = True
                                break
                        if variant_updated:
                            sqlalchemy.orm.attributes.flag_modified(post, "variants")
                            session.add(post)

                session.commit()
                
                # Opcional: Notificar al admin usando AppState
                state = await rx.get_state(AppState)
                await state.notify_admin_of_new_purchase()

            elif status in ["DECLINED", "ERROR", "VOIDED"]:
                purchase.status = PurchaseStatus.PENDING_CONFIRMATION # O un nuevo estado "FAILED"
                session.add(purchase)
                session.commit()
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error procesando el webhook de Wompi: {e}")
        return {"error": "Error interno"}, 500