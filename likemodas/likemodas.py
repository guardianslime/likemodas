# likemodas/likemodas.py (ARCHIVO PRINCIPAL CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth

from.state import AppState
from starlette.responses import Response
# --- Módulos de la aplicación ---
from.auth import pages as auth_pages
from.pages import search_results, category_page
from.blog import (
    blog_public_page_content, blog_public_detail_content, blog_post_list_content,
    blog_post_detail_content, blog_post_add_content, blog_post_edit_content
)
from.cart import page as cart_page
from.purchases import page as purchases_page
from.admin import page as admin_page
from.contact import page as contact_page
from. import navigation
from.account import shipping_info as shipping_info_module
from.ui.base import base_page
from. import models

# Estado específico para la página de inicio para manejar su carga
class HomePageState(AppState):
    @rx.event
    def on_load_main(self):
        self.current_category = ""
        yield AppState.on_load 

def index_content() -> rx.Component:
    return blog_public_page_content()

# --- Configuración de la App ---
app = rx.App()

# --- Definición de Rutas ---
app.add_page(base_page(index_content()), route="/", on_load=HomePageState.on_load_main)
# app.add_page(base_page(category_page.category_content()), route="/category/[cat_name]", title="Categoría", on_load=AppState.load_posts_and_set_category)
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")

# Rutas de Autenticación
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token)
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token)

# Rutas del Blog/Galería
app.add_page(base_page(blog_public_detail_content()), route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[id]", title="Detalle del Producto", on_load=AppState.on_load_public_detail)

# Rutas de Cuenta, Carrito y Compras
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)

# Rutas de Administración
# app.add_page(base_page(blog_post_list_content()), route=navigation.routes.BLOG_POSTS_ROUTE, on_load=AppState.load_admin_posts)
# app.add_page(base_page(blog_post_detail_content()), route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=AppState.get_post_detail)
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE)
# app.add_page(base_page(blog_post_edit_content()), route="/blog/[blog_id]/edit", on_load=AppState.on_load_edit)
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Confirmar Pagos", on_load=AppState.load_pending_purchases)
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_confirmed_purchases)
app.add_page(base_page(contact_page.contact_entries_list_content()), route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=AppState.load_entries)



# Este endpoint especial se añade al API de FastAPI subyacente de Reflex.
def health_check():
    """
    Endpoint simple para que Railway (o cualquier servicio) verifique 
    que la aplicación está activa y respondiendo.
    """
    from starlette.responses import Response
    return Response(status_code=200, content="OK")

# 2. Añade la ruta al objeto app usando el método add_api_route
app.add_api_route("/health", health_check, methods=["GET"])
