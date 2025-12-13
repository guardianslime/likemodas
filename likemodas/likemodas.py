# likemodas/likemodas.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse # <--- Importante para assetlinks
import reflex as rx
import reflex_local_auth

# Módulos internos de la aplicación
from .api import webhooks, tasks as api_tasks
from .api import mobile_api
from .state import AppState
from .ui.base import base_page
from . import navigation

# Vistas de autenticación
from .auth import pages as auth_pages
from .auth.tfa_verify_page import tfa_verify_page_content

# Vistas de la cuenta de CLIENTE
from .account import profile_page as user_profile_page
from .account import shipping_info as shipping_info_module
from .account import saved_posts as saved_posts_module

# Importamos la función 'display_settings_page' directamente
from .account.display_settings_page import display_settings_page

# Vistas de ADMINISTRADOR
from .admin import page as admin_page
from .admin import finance_page
from .admin.profile_page import admin_profile_page_content
from .admin.my_location_page import my_location_page_content
from .admin.store_page import admin_store_page
from .admin.tickets_page import admin_tickets_page_content
from .admin.users_page import user_management_page
from .admin import employees_page
from .admin.reports_page import reports_page_content

# Vistas de Blog y Productos
from .blog import blog_admin_page, blog_post_add_content
from .pages import landing, seller_page

# Vistas del proceso de compra
from .cart import page as cart_page
from .purchases import page as purchases_page
from .pages import payment_status, payment_pending, processing_payment
from likemodas.pages.delete_account_info import delete_account_info
from .pages.legal.terms_page import terms_page
from .pages.legal.privacy_page import privacy_page
from .pages.legal.cookies_page import cookies_page
from .invoice import page as invoice_page
from .invoice.state import InvoiceState
from .returns import page as returns_page

# Configuración de FastAPI
fastapi_app = FastAPI(title="API extendida de Likemodas")


fastapi_app.include_router(webhooks.router)
fastapi_app.include_router(api_tasks.router)
fastapi_app.include_router(mobile_api.router)

app = rx.App(
    head_components=[
        rx.el.meta(name="description", content="Compra lo mejor en moda..."),
        rx.el.meta(name="keywords", content="likemodas, ropa, calzado..."),
        rx.el.meta(property="og:title", content="Likemodas"),
        rx.el.meta(property="og:description", content="Descubre nuestra colección."),
        rx.el.meta(property="og:image", content="/logo.png"),
    ],
    style={
        "font_family": "Arial, sans-serif",
        ".ToastViewport": {"z_index": "99999 !important"},
    },
    api_transformer=fastapi_app
)

# --- LÓGICA DE REDIRECCIÓN WEB (PUENTE) ---
class DeepLinkState(rx.State):
    @rx.var
    def product_id_from_url(self) -> str:
        return self.router.page.params.get("product_id", "")

    def redirect_to_modal(self):
        p_id = self.product_id_from_url
        if p_id:
            # Redirige a la home cargando el modal
            return rx.redirect(f"/?product_id_to_load={p_id}")
        return rx.redirect("/")

@rx.page(route="/product/[product_id]", on_load=DeepLinkState.redirect_to_modal)
def product_deep_link_page():
    # Página invisible que redirige si no se abre la App
    return rx.center(
        rx.spinner(size="3", color="violet"),
        height="100vh", width="100%"
    )

# --- DEFINICIÓN DE PÁGINAS ---
app.add_page(base_page(landing.landing_content()), route="/", on_load=AppState.load_main_page_data, title="Likemodas - Inicio")
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(tfa_verify_page_content()), route="/verify-2fa", title="Verificación 2FA")
app.add_page(base_page(seller_page.seller_page_content()), route="/vendedor", on_load=AppState.on_load_seller_page, title="Publicaciones del Vendedor")

app.add_page(user_profile_page.profile_page_content(), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(shipping_info_module.shipping_info_content(), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(saved_posts_module.saved_posts_content(), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(display_settings_page(), route="/my-account/display-settings", title="Configuración de Visualización")

app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(purchases_page.purchase_history_content(), route="/my-purchases", title="Mis Compras", on_load=AppState.on_load_purchases_page)
app.add_page(base_page(payment_status.payment_status_page()), route="/payment-status", title="Estado del Pago")
app.add_page(base_page(payment_pending.payment_pending_page()), route="/payment-pending", title="Pago Pendiente")
app.add_page(processing_payment.processing_payment_page(), route="/processing-payment", on_load=AppState.start_sistecredito_polling, title="Procesando Pago")

app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=AppState.on_load_invoice_page, title="Factura")
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")

app.add_page(admin_profile_page_content(), route="/admin/profile", title="Perfil de Administrador", on_load=AppState.on_load_profile_page)
app.add_page(my_location_page_content(), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones", on_load=[AppState.sync_user_context, AppState.load_mis_publicaciones])
app.add_page(base_page(finance_page.finance_page_content()), route="/admin/finance", on_load=AppState.on_load_finance_data, title="Finanzas")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=[AppState.on_load_admin_store, AppState.process_qr_url_on_load], title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(base_page(employees_page.employees_management_page()), route="/admin/employees", on_load=AppState.load_empleados, title="Gestión de Empleados")
app.add_page(base_page(reports_page_content()), route="/admin/reports", on_load=AppState.load_admin_reports, title="Gestión de Reportes")

app.add_page(terms_page, route="/terms", title="Términos y Condiciones")
app.add_page(privacy_page, route="/privacy", title="Política de Privacidad")
app.add_page(cookies_page, route="/cookies", title="Política de Cookies")
app.add_page(delete_account_info, route="/delete-account-info", title="Eliminar Cuenta")