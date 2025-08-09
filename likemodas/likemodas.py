# likemodas/likemodas.py (ARCHIVO PRINCIPAL CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth

from .state import AppState
from .ui.base import base_page  # Importamos el layout base

# --- Módulos de la aplicación (páginas) ---
from .auth import pages as auth_pages
from .pages import search_results, category_page
from .blog import (
    blog_public_page_content, 
    blog_admin_page, 
    blog_public_detail_content,
    blog_post_add_content
)
from .cart import page as cart_page
from .purchases import page as purchases_page
from .admin import page as admin_page
from .contact import page as contact_page
from .account import shipping_info as shipping_info_module
from . import navigation

# --- Configuración de la App ---
# Usamos el layout `base_page` como plantilla para todas las páginas.
# Si alguna página no debe usarlo, se añade con app.add_page(componente)
# en lugar de app.add_page(base_page(componente)).
app = rx.App(state=AppState, style={"font_family": "Arial, sans-serif"})

# --- Definición de Rutas ---

# Ruta principal (la galería de productos)
# Esta es la única función que debe estar en la ruta "/".
# Eliminamos la función `index()` y `app.add_page(index)` para evitar conflictos.
app.add_page(
    base_page(blog_public_page_content()),
    route="/",
    on_load=AppState.on_load  # Evento para cargar productos en la página principal
)

# Rutas de Autenticación
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")

# Rutas de Blog/Galería y Productos
app.add_page(base_page(blog_public_detail_content()), route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[id]", title="Detalle del Producto", on_load=AppState.on_load_public_detail)
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")

# Rutas de Cuenta, Carrito y Compras
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)

# --- Rutas de Administración ---
# Esta es la ruta que estamos arreglando.
app.add_page(base_page(blog_admin_page()), route="/my-blog-posts", title="Mis Publicaciones")

# Ruta para añadir nuevos posts/productos
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")

# Otras rutas de Admin
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Confirmar Pagos", on_load=AppState.load_pending_purchases)
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_confirmed_purchases)
app.add_page(base_page(contact_page.contact_entries_list_content()), route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=AppState.load_entries, title="Mensajes de Contacto")