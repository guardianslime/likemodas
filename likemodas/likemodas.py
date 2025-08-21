# likemodas/likemodas.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth

# --- ✨ AÑADE ESTAS LÍNEAS ---
from fastapi.responses import StreamingResponse
# --- ✨ LÍNEA MODIFICADA ---
# ANTES: from reflex_local_auth.auth_session import AuthSession
from reflex_local_auth.auth_session import LocalAuthSession # <-- AHORA
from .services.invoice_service import generate_invoice_pdf
from .models import PurchaseModel, UserRole
import io

from .state import AppState
from .ui.base import base_page

from .auth import pages as auth_pages
# Asegúrate de que 'landing' esté importado desde .pages
from .pages import landing, search_results, category_page, seller_page # <-- Añade seller_page

from .blog import (
    blog_public_page_content, 
    blog_admin_page, 
    blog_post_add_content
)
from .cart import page as cart_page
from .purchases import page as purchases_page
from .admin import page as admin_page
from .admin.store_page import admin_store_page
from .admin.users_page import user_management_page
from .contact import page as contact_page
from .account import shipping_info as shipping_info_module
from .account import saved_posts as saved_posts_module # <-- AÑADE ESTA IMPORTACIÓN
from . import navigation

app = rx.App(style={"font_family": "Arial, sans-serif"})


# --- ✨ LÍNEA MODIFICADA ---
# ANTES: def get_invoice(purchase_id: int, auth_session: AuthSession = rx.Depends(reflex_local_auth.auth_session)):
def get_invoice(purchase_id: int, auth_session: LocalAuthSession = rx.Depends(reflex_local_auth.auth_session)): # <-- AHORA
    """
    Endpoint para generar y descargar una factura en PDF de forma segura.
    """
    if not auth_session.user:
        return {"error": "No autenticado"}, 401

    with rx.session() as session:
        # Obtenemos la compra con todas sus relaciones cargadas
        purchase = session.exec(
            rx.select(PurchaseModel)
            .options(
                rx.subqueryload(PurchaseModel.items).subqueryload("blog_post"),
                rx.subqueryload(PurchaseModel.userinfo)
            )
            .where(PurchaseModel.id == purchase_id)
        ).one_or_none()

        if not purchase:
            return {"error": "Factura no encontrada"}, 404

        # Comprobación de seguridad: solo el dueño o un admin pueden descargarla
        user_info = purchase.userinfo
        if user_info.user_id != auth_session.user.id and user_info.role != UserRole.ADMIN:
            return {"error": "No autorizado"}, 403
        
        # Generamos el PDF
        pdf_bytes = generate_invoice_pdf(purchase)

        # Preparamos la respuesta para la descarga
        filename = f"Factura-Likemodas-{purchase.id}.pdf"
        headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
        
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)



# --- Ruta principal (la galería de productos) ---
app.add_page(
    # ANTES: base_page(blog_public_page_content()),
    # AHORA:
    base_page(landing.landing_content()),
    route="/",
    on_load=AppState.on_load_main_page,
    title="Likemodas | Inicio"
)

# AÑADE ESTA RUTA (puede ser después de las de búsqueda)
app.add_page(
    base_page(seller_page.seller_page_content()), 
    route="/vendedor",  # <-- Ruta fija, sin corchetes
    on_load=AppState.on_load_seller_page,
    title="Publicaciones del Vendedor"
)


# --- Rutas de Autenticación ---
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")

# --- Rutas de Búsqueda ---
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")

# --- Rutas de Cuenta, Carrito y Compras ---
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts_module.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)

# --- Rutas de Administración ---
app.add_page(
    base_page(blog_admin_page()), 
    route="/blog", 
    title="Mis Publicaciones"
)
app.add_page(
    base_page(user_management_page()), 
    route="/admin/users", 
    on_load=AppState.load_all_users,
    title="Gestión de Usuarios"
)
app.add_page(
    base_page(blog_post_add_content()), 
    route=navigation.routes.BLOG_POST_ADD_ROUTE, 
    title="Añadir Producto"
)
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Confirmar Pagos", on_load=AppState.load_pending_purchases)
app.add_page(
    base_page(admin_store_page()), 
    route="/admin/store", 
    on_load=AppState.on_load_admin_store,
    title="Admin | Tienda"
)
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_confirmed_purchases)
app.add_page(base_page(contact_page.contact_entries_list_content()), route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=AppState.load_entries, title="Mensajes de Contacto")

# --- ✨ 2. REGISTRA LA RUTA DE LA API MANUALMENTE AL FINAL ✨ ---
app.add_api_route("/api/invoice/{purchase_id}", get_invoice, methods=["GET"])