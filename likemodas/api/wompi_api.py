# likemodas/api/wompi_api.py (Versión con Biblioteca Wompi)

import os
import reflex as rx
from fastapi import FastAPI, Request
import sqlalchemy
from sqlmodel import select
from datetime import datetime, timezone
import wompi # 1. Importamos la nueva biblioteca

from ..models import PurchaseModel, PurchaseStatus, BlogPostModel, PurchaseItemModel, UserInfo
from ..state import AppState

# 2. Creamos una aplicación FastAPI independiente para manejar las rutas
wompi_api = FastAPI()

# 3. Configuramos el cliente de Wompi con tus llaves del .env
wompi_client = wompi.Client(
    public_key=os.getenv("WOMPI_PUBLIC_KEY"),
    private_key=os.getenv("WOMPI_PRIVATE_KEY"),
)

@wompi_api.post("/wompi/create_checkout_session")
async def create_wompi_checkout(request: Request) -> dict:
    """
    Crea la transacción en Wompi usando la biblioteca y devuelve el enlace de pago.
    """
    try:
        body = await request.json()
        purchase_id = body.get("purchase_id")
        amount_cop = body.get("amount")
        customer_email = body.get("customer_email")
        redirect_url = body.get("redirect_url")

        # 4. Usamos la biblioteca para crear la transacción. ¡Mucho más fácil!
        transaction = wompi_client.transactions.create(
            amount_in_cents=int(float(amount_cop) * 100),
            currency="COP",
            customer_email=customer_email,
            reference=f"likemodas-purchase-{purchase_id}",
            redirect_url=redirect_url,
        )
        
        # El enlace de pago ahora está en el presigned_acceptance
        payment_url = transaction.payment_method.extra.presigned_acceptance.permalink
        return {"payment_url": payment_url}

    except Exception as e:
        print(f"Error creando la transacción de Wompi: {e}")
        return {"error": "Error al comunicarse con Wompi."}, 500

@wompi_api.post("/wompi/webhook")
async def wompi_webhook(request: Request) -> dict:
    """
    Recibe y procesa las notificaciones de Wompi.
    """
    try:
        payload = await request.json()
        print(f"Webhook de Wompi recibido: {payload}")

        event = wompi.Event(payload) # La biblioteca puede parsear el evento por nosotros
        
        # 5. Opcional pero recomendado: Verificar la firma del evento
        # event_secret = os.getenv("WOMPI_EVENTS_SECRET")
        # if not event.is_authentic(event_secret):
        #     return {"error": "Firma inválida"}, 400

        transaction = event.data.transaction
        if event.event == "transaction.updated" and transaction.status == "APPROVED":
            reference = transaction.reference
            purchase_id = int(reference.split("-")[-1])

            with rx.session() as session:
                # La lógica para actualizar la base de datos es la misma
                purchase = session.get(PurchaseModel, purchase_id)
                if purchase and purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    session.add(purchase)

                    # Deducir stock...
                    for item in purchase.items:
                        post = session.get(BlogPostModel, item.blog_post_id)
                        if post:
                            variant_updated = False
                            for variant in post.variants:
                                if variant.get("attributes") == item.selected_variant:
                                    variant["stock"] -= item.quantity
                                    variant_updated = True
                                    break
                            if variant_updated:
                                sqlalchemy.orm.attributes.flag_modified(post, "variants")
                                session.add(post)
                    
                    session.commit()
                    state = await rx.get_state(AppState)
                    await state.notify_admin_of_new_purchase()

        return {"status": "ok"}
    except Exception as e:
        print(f"Error procesando el webhook de Wompi: {e}")
        return {"error": "Error interno"}, 500