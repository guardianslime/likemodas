# likemodas/likemodas.py

from fastapi import FastAPI
import reflex as rx
import reflex_local_auth
import os
from dotenv import load_dotenv

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

# Páginas legales (Si estas te dan error también, avísame para ajustar su importación)
from .pages import terms_page, privacy_page

load_dotenv()

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    db_url=os.getenv("DATABASE_URL"),
    api_url=os.getenv("API_URL", "https://api.likemodas.com"),
    deploy_url=os.getenv("DEPLOY_URL", "https://www.likemodas.com"),
    
    # --- CONFIGURACIÓN DE CORS ---
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "*", 
    ],
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)

app = rx.App()

# --- RUTAS DE LA APLICACIÓN ---

# 1. Ruta Principal (Landing / Home)
app.add_page(base_page(landing.landing_content()), route=navigation.routes.HOME_ROUTE, title="Inicio")

# 2. RUTA DEEP LINK (NUEVA - INTEGRADA)
# Captura el tráfico de https://likemodas.com/product/123 y abre el modal
app.add_page(
    base_page(landing.landing_content()), 
    route="/product/[product_id_url]", 
    on_load=AppState.check_deep_link 
)

# Rutas de Autenticación
app.add_page(base_page(auth_pages.login_page()), route=navigation.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.register_page()), route=navigation.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(tfa_verify_page_content()), route="/verify-2fa", title="Verificación 2FA")

# Rutas de Cuenta de Usuario
app.add_page(base_page(user_profile_page.profile_page_content()), route=navigation.routes.PROFILE_ROUTE, on_load=AppState.check_auth, title="Mi Perfil")
app.add_page(base_page(shipping_info_module.shipping_info_page()), route=navigation.routes.SHIPPING_INFO_ROUTE, on_load=AppState.check_auth, title="Datos de Envío")
app.add_page(base_page(saved_posts_module.saved_posts_page()), route=navigation.routes.SAVED_POSTS_ROUTE, on_load=AppState.check_auth, title="Guardados")
app.add_page(base_page(display_settings_page()), route="/account/display-settings", on_load=AppState.check_auth, title="Configuración de Visualización")

# Rutas Públicas de Vendedor
app.add_page(base_page(seller_page.seller_page_content()), route="/seller/[user_id]", on_load=AppState.load_seller_page, title="Perfil del Vendedor")

# Rutas de Administrador
app.add_page(base_page(admin_page.dashboard_content()), route=navigation.routes.ADMIN_DASHBOARD_ROUTE, on_load=AppState.check_admin_access, title="Panel Admin")
app.add_page(base_page(admin_profile_page_content()), route="/admin/profile", on_load=AppState.check_admin_access, title="Perfil Admin")
app.add_page(base_page(my_location_page_content()), route="/admin/my-location", on_load=AppState.check_admin_access, title="Mi Ubicación")
app.add_page(base_page(finance_page.finance_content()), route=navigation.routes.ADMIN_FINANCE_ROUTE, on_load=AppState.load_finance_data, title="Finanzas")
app.add_page(base_page(blog_admin_page.blog_admin_content()), route=navigation.routes.BLOG_ADMIN_ROUTE, on_load=AppState.load_blog_posts_admin, title="Gestión de Productos")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=[AppState.on_load_admin_store, AppState.process_qr_url_on_load], title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(base_page(employees_page.employees_management_page()), route="/admin/employees", on_load=AppState.load_empleados, title="Gestión de Empleados")
app.add_page(base_page(reports_page_content()), route="/admin/reports", on_load=AppState.load_admin_reports, title="Gestión de Reportes")

# Páginas Legales
app.add_page(terms_page.terms_page_content(), route="/terms", title="Términos y Condiciones")
app.add_page(privacy_page.privacy_page_content(), route="/privacy", title="Política de Privacidad")

# Incluir Routers de API
app.api.include_router(webhooks.router)
app.api.include_router(mobile_api.router)