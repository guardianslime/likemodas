# likemodas/likemodas.py (Versión Final y Funcional)

import reflex as rx
import reflex_local_auth
import json
import httpx
import hashlib
import os
import sqlalchemy
from fastapi import Request as FastAPIRequest
from sqlmodel import select
from datetime import datetime, timezone

# Importaciones del proyecto
from likemodas.ui.base import base_page
from likemodas.state import AppState
from likemodas.invoice.state import InvoiceState
from likemodas.models import PurchaseModel, PurchaseStatus, BlogPostModel, PurchaseItemModel
from likemodas import navigation

# Importaciones de páginas (abreviado por claridad)
from likemodas.account import profile_page, saved_posts, shipping_info
from likemodas.admin import page as admin_page
from likemodas.admin.profile_page import seller_profile_page
from likemodas.admin.store_page import admin_store_page
from likemodas.admin.tickets_page import admin_tickets_page_content
from likemodas.admin.users_page import user_management_page
from likemodas.auth import pages as auth_pages
from likemodas.blog import blog_admin_page, blog_post_add_content
from likemodas.cart import page as cart_page
from likemodas.contact import page as contact_page
from likemodas.invoice import page as invoice_page
from likemodas.pages import landing, search_results, seller_page
from likemodas.purchases import page as purchases_page
from likemodas.returns import page as returns_page

# --- 1. Definición de la App ---
app = rx.App(
    style={"font_family": "Arial, sans-serif"},
)

# --- 2. Lógica y Rutas de la API de Wompi ---
WOMPI_API_URL = "https://sandbox.wompi.co/v1"
WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY")
WOMPI_INTEGRITY_SECRET = os.getenv("WOMPI_INTEGRITY_SECRET")

@app._api("/api/wompi/create_checkout_session")
async def create_wompi_checkout_endpoint(scope, receive, send):
    # Verificamos que la petición sea POST
    if scope['method'] != 'POST':
        response = rx.Response(content="Method Not Allowed", status_code=405)
        await response(scope, receive, send)
        return

    request = FastAPIRequest(scope, receive)
    try:
        body = await request.json()
        purchase_id = body.get("purchase_id")
        amount_cop = body.get("amount")
        customer_email = body.get("customer_email")
        redirect_url = body.get("redirect_url")

        if not all([purchase_id, amount_cop, customer_email, redirect_url]):
            response = rx.Response(content=json.dumps({"error": "Faltan datos"}), status_code=400, media_type="application/json")
            await response(scope, receive, send)
            return

        amount_in_cents = int(float(amount_cop) * 100)
        reference = f"likemodas-purchase-{purchase_id}"
        concatenation = f"{reference}{amount_in_cents}COP{WOMPI_INTEGRITY_SECRET}"
        signature = hashlib.sha256(concatenation.encode("utf-8")).hexdigest()

        wompi_payload = {
            "currency": "COP", "amount_in_cents": amount_in_cents, "reference": reference,
            "signature:integrity": signature, "customer_email": customer_email, "redirect_url": redirect_url,
        }

        async with httpx.AsyncClient() as client:
            wompi_response = await client.post(
                f"{WOMPI_API_URL}/checkouts",
                headers={"Authorization": f"Bearer {WOMPI_PUBLIC_KEY}"},
                json=wompi_payload
            )
            wompi_response.raise_for_status()
            wompi_data = wompi_response.json()
        
        response = rx.Response(content=json.dumps({"checkout_id": wompi_data.get("data", {}).get("id")}), status_code=200, media_type="application/json")

    except Exception as e:
        print(f"Error en create_checkout_session: {e}")
        response = rx.Response(content=json.dumps({"error": "Error interno"}), status_code=500, media_type="application/json")
    
    await response(scope, receive, send)

@app._api("/api/wompi/webhook")
async def wompi_webhook_endpoint(scope, receive, send):
    # Verificamos que la petición sea POST
    if scope['method'] != 'POST':
        response = rx.Response(content="Method Not Allowed", status_code=405)
        await response(scope, receive, send)
        return

    request = FastAPIRequest(scope, receive)
    try:
        payload = await request.json()
        print(f"Webhook de Wompi recibido: {payload}")
        
        transaction_data = payload.get("data", {}).get("transaction", {})
        status = transaction_data.get("status")
        reference = transaction_data.get("reference")

        if reference and reference.startswith("likemodas-purchase-"):
            purchase_id = int(reference.split("-")[-1])
            with rx.session() as session:
                purchase = session.get(PurchaseModel, purchase_id)
                if purchase and status == "APPROVED" and purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    session.add(purchase)

                    for item in purchase.items:
                        post = session.get(BlogPostModel, item.blog_post_id)
                        if post:
                            for variant in post.variants:
                                if variant.get("attributes") == item.selected_variant:
                                    variant["stock"] -= item.quantity
                                    sqlalchemy.orm.attributes.flag_modified(post, "variants")
                                    session.add(post)
                                    break
                    
                    session.commit()
                    state = await rx.get_state(AppState)
                    await state.notify_admin_of_new_purchase()

        response = rx.Response(content=json.dumps({"status": "ok"}), status_code=200, media_type="application/json")

    except Exception as e:
        print(f"Error procesando webhook: {e}")
        response = rx.Response(content=json.dumps({"error": "Error interno"}), status_code=500, media_type="application/json")

    await response(scope, receive, send)

# --- 3. Añadimos todas las páginas al objeto 'app' ---
app.add_page(
    base_page(landing.landing_content()),
    route="/",
    on_load=AppState.load_main_page_data,
    title="Likemodas | Inicio"
)
app.add_page(
    base_page(seller_page.seller_page_content()), 
    route="/vendedor",
    on_load=AppState.on_load_seller_page,
    title="Publicaciones del Vendedor"
)
app.add_page(
    base_page(search_results.search_results_content()), 
    route="/search-results", 
    title="Resultados de Búsqueda"
)
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(profile_page.profile_page_content()), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(seller_profile_page()), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=AppState.on_load_admin_store, title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=InvoiceState.on_load_invoice_page, title="Factura")