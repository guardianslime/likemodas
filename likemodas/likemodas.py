# likemodas/likemodas.py

from fastapi import FastAPI
import reflex as rx

# --- 🛠️ PARCHE DE COMPATIBILIDAD (AÑADIR ESTO) 🛠️ ---
# Esto engaña a reflex-local-auth para que funcione con tu versión actual de Reflex
if not hasattr(rx, "cached_var"):
    rx.cached_var = rx.var
# ----------------------------------------------------

import reflex_local_auth  # <--- Este import debe ir DESPUÉS del parche

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

# Importamos las páginas legales
from .pages.legal.terms_page import terms_page
from .pages.legal.privacy_page import privacy_page
from .pages.legal.cookies_page import cookies_page

# Vistas de soporte y facturas
from .invoice import page as invoice_page
from .invoice.state import InvoiceState
from .returns import page as returns_page

# Configuración del backend de FastAPI
fastapi_app = FastAPI(title="API extendida de Likemodas")
fastapi_app.include_router(webhooks.router)
fastapi_app.include_router(api_tasks.router)
fastapi_app.include_router(mobile_api.router)

# Configuración de la aplicación Reflex
app = rx.App(
    head_components=[
        rx.el.meta(name="description", content="Compra lo mejor en moda, calzado y accesorios en Likemodas. Envíos a toda Colombia. Calidad y estilo al mejor precio."),
        rx.el.meta(name="keywords", content="likemodas, ropa, calzado, colombia, moda, tienda online, zapatillas, bolsos"),
        rx.el.meta(property="og:title", content="Likemodas - Estilo y Calidad"),
        rx.el.meta(property="og:description", content="Descubre nuestra colección exclusiva."),
        rx.el.meta(property="og:image", content="/logo.png"),
    ],
    style={
        "font_family": "Arial, sans-serif",
        ".ToastViewport": {
            "z_index": "99999 !important",
        },
    },
    api_transformer=fastapi_app
)

# --- PÁGINA TRAMPOLÍN (CORREGIDA) ---
# Esta función gestiona la apertura de la app mediante esquema personalizado
# --- PÁGINA TRAMPOLÍN (MEJORADA CON BOTÓN MANUAL) ---
def deep_link_handler():
    # 1. Obtener ID
    current_id = AppState.router.page.params.get("deep_id", "")
    
    # 2. Construir link directo a la app (Plan B)
    # Usamos to_string() para evitar errores de tipo
    app_scheme_url = "likemodas://product/" + current_id.to_string()
    
    # 3. Construir el script de redirección automática
    # Intentará abrir la app apenas cargue
    script_code = "window.location.href = '" + app_scheme_url + "';"

    return rx.center(
        # Intentar redirección automática (invisible)
        rx.script(script_code),
        
        rx.vstack(
            rx.heading("¡Producto Encontrado!", size="6", color="violet"),
            rx.text("Intentando abrir la App...", color="gray"),
            
            rx.spinner(color="violet", size="3"),
            
            rx.divider(),
            
            # --- BOTÓN MANUAL (LA SOLUCIÓN) ---
            # Si Chrome bloquea la redirección automática, este botón SIEMPRE funcionará
            rx.link(
                rx.button(
                    "Abrir en la App",
                    size="4",
                    color_scheme="violet",
                    width="100%"
                ),
                href=app_scheme_url, # Clic manual -> Chrome permite abrir la App
                is_external=True
            ),
            
            rx.text("o", color="gray", size="1"),
            
            # Opción para quedarse en la web
            rx.button(
                "Ver en el Navegador",
                variant="outline",
                on_click=AppState.check_deep_link, # Carga el modal en la web
                width="100%"
            ),
            
            spacing="4",
            align="center",
            padding="2em",
            bg="white",
            border_radius="1em",
            box_shadow="lg"
        ),
        height="100vh",
        width="100%",
        bg="#f5f5f5"
    )

# --- ENDPOINT DE SEGURIDAD (ASSETLINKS) ---
# Sirve el archivo de verificación para Android App Links (si el custom scheme falla)
@fastapi_app.get("/.well-known/assetlinks.json") 
async def assetlinks_endpoint():
    return [
      {
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
          "namespace": "android_app",
          "package_name": "com.likemodas.app",
          "sha256_cert_fingerprints": [
            "E9:BC:A9:3D:0D:95:42:00:1D:C1:EC:F1:11:1A:6E:EF:70:19:61:6F:9B:D5:DF:97:0F:89:5B:6A:CA:6B:38:F8"
          ]
        }
      }
    ]

# --- REGISTRO DE RUTAS ---

# Rutas Públicas y de Autenticación
app.add_page(base_page(landing.landing_content()), route="/", on_load=AppState.load_main_page_data, title="Likemodas - Inicio")

# Añade esta línea donde defines tus páginas
app.add_page(
    landing.landing_content, 
    route="/product/[deep_id]",  # Captura el ID de la URL
    on_load=AppState.handle_deep_link_route # Ejecuta la lógica al cargar
)



app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(tfa_verify_page_content()), route="/verify-2fa", title="Verificación 2FA")
app.add_page(base_page(seller_page.seller_page_content()), route="/vendedor", on_load=AppState.on_load_seller_page, title="Publicaciones del Vendedor")

# Rutas de la Cuenta de CLIENTE
app.add_page(user_profile_page.profile_page_content(), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(shipping_info_module.shipping_info_content(), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(saved_posts_module.saved_posts_content(), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(display_settings_page(), route="/my-account/display-settings", title="Configuración de Visualización")

# Rutas del Proceso de Compra
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(purchases_page.purchase_history_content(), route="/my-purchases", title="Mis Compras", on_load=AppState.on_load_purchases_page)
app.add_page(base_page(payment_status.payment_status_page()), route="/payment-status", title="Estado del Pago")
app.add_page(base_page(payment_pending.payment_pending_page()), route="/payment-pending", title="Pago Pendiente")
app.add_page(processing_payment.processing_payment_page(), route="/processing-payment", on_load=AppState.start_sistecredito_polling, title="Procesando Pago")

# Rutas de Soporte y Facturas
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=AppState.on_load_invoice_page, title="Factura")
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")

# Rutas del Panel de ADMINISTRADOR
app.add_page(admin_profile_page_content(), route="/admin/profile", title="Perfil de Administrador", on_load=AppState.on_load_profile_page)
app.add_page(my_location_page_content(), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(
    base_page(blog_admin_page()), 
    route="/blog", 
    title="Mis Publicaciones",
    on_load=[
        AppState.sync_user_context,
        AppState.load_mis_publicaciones
    ]
)
app.add_page(base_page(finance_page.finance_page_content()), route="/admin/finance", on_load=AppState.on_load_finance_data, title="Finanzas")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=[AppState.on_load_admin_store, AppState.process_qr_url_on_load], title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(base_page(employees_page.employees_management_page()), route="/admin/employees", on_load=AppState.load_empleados, title="Gestión de Empleados")
app.add_page(base_page(reports_page_content()), route="/admin/reports", on_load=AppState.load_admin_reports, title="Gestión de Reportes")

# Páginas Legales
app.add_page(terms_page, route="/terms", title="Términos y Condiciones")
app.add_page(privacy_page, route="/privacy", title="Política de Privacidad")
app.add_page(cookies_page, route="/cookies", title="Política de Cookies")

# Eliminar cuenta
app.add_page(delete_account_info, route="/delete-account-info", title="Eliminar Cuenta")

# --- AL FINAL DE likemodas/likemodas.py ---
from fastapi.responses import JSONResponse
from .api.tasks import reconcile_pending_payments # Aseguramos la importación
from likemodas.db.session import get_session # Necesario para la base de datos

async def reconcile_payments_task(request):
    try:
        # 1. Obtenemos el secreto de los parámetros de la URL (?secret=...)
        # Si no envías secreto en la URL, el script de tasks.py lo rechazará.
        secret = request.query_params.get("secret")
        
        # 2. Obtenemos una sesión de base de datos manualmente
        # ya que Starlette.add_route no maneja Depends() automáticamente
        session_gen = get_session()
        session = next(session_gen)
        
        # 3. Llamamos a la función con el nombre CORRECTO: reconcile_pending_payments
        resultado = await reconcile_pending_payments(secret=secret, session=session)
        return JSONResponse(content=resultado)
        
    except Exception as e:
        import logging
        logging.error(f"Error en reconcile_payments: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Fallo interno", "detalle": str(e)}
        )

# Registramos las rutas
app._api.add_route("/.well-known/assetlinks.json", assetlinks_endpoint)
# Usamos métodos GET y POST para que sea compatible con cualquier Cron-job
app._api.add_route("/tasks/reconcile-payments", reconcile_payments_task, methods=["GET", "POST"])