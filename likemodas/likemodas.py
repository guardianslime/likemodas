import reflex as rx
import reflex_local_auth
from rxconfig import config

# --- Módulos específicos (los importamos para tener acceso a las funciones de contenido) ---
from .auth import pages as auth_pages
from .blog import page as blog_page, public_detail, list as blog_list, detail as blog_detail, add as blog_add, edit as blog_edit
from .cart import page as cart_page
from .pages import search_results, about, pricing, dashboard, category_page
from .purchases import page as purchases_page
from .contact import page as contact_page
from .account import page as account_page_module, shipping_info
from .ui.base import base_page

# --- Componente de Enrutamiento Principal ---
def frontend() -> rx.Component:
    """
    Este es el único componente de página. Decide qué contenido mostrar
    basándose en la URL actual, usando rx.match.
    """
    return base_page(  # Todo se envuelve en base_page para tener la lógica de auth y el tema
        rx.match(
            rx.State.router.page.path,
            # --- Rutas Públicas ---
            ("/", blog_page.blog_public_page()),
            ("/blog/page", blog_page.blog_public_page()),
            ("/about", about.about_page()),
            ("/pricing", pricing.pricing_page()),
            ("/contact", contact_page.contact_page()),
            ("/search-results", search_results.search_results_page()),
            
            # --- Rutas de Usuario Autenticado ---
            ("/dashboard", dashboard.dashboard_component()),
            ("/cart", cart_page.cart_page()),
            ("/my-purchases", purchases_page.purchase_history_page()),
            ("/my-account/shipping-info", shipping_info.shipping_info_page()),
            
            # --- Rutas de Administrador ---
            ("/blog", blog_list.blog_post_list_page()),
            ("/blog/add", blog_add.blog_post_add_page()),
            ("/admin/confirm-payments", cart_page.admin_confirm_page()),
            ("/admin/payment-history", cart_page.payment_history_page()),
            ("/contact/entries", contact_page.contact_entries_list_page()),
            
            # Por defecto, si no coincide, muestra la página de inicio
            (blog_page.blog_public_page())
        )
    )

# --- CONFIGURACIÓN DE LA APP ---
app = rx.App()

# --- REGISTRO DE PÁGINAS ---
# Añadimos la página raíz para que maneje todas las rutas.
app.add_page(frontend, route="/[[...splat]]")

# Añadimos las páginas de autenticación que tienen su propia lógica y no usan base_page de la misma manera
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)

# --- Páginas dinámicas que necesitan su propio 'on_load' ---
# Aunque 'frontend' las renderiza, necesitamos registrar la ruta para que 'on_load' funcione.
from .blog.state import CommentState
from .pages.category_page import CategoryPageState

app.add_page(frontend, route="/blog-public/[blog_public_id]", on_load=CommentState.on_load)
app.add_page(frontend, route="/category/[cat_name]", on_load=CategoryPageState.load_category_posts)

# Aquí puedes añadir otras páginas dinámicas de admin si es necesario
from .blog.state import BlogPostState, BlogEditFormState
app.add_page(frontend, route="/blog/[blog_id]", on_load=BlogPostState.get_post_detail)
app.add_page(frontend, route="/blog/[blog_id]/edit", on_load=BlogEditFormState.on_load_edit)