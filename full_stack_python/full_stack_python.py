import reflex as rx
import reflex_local_auth

from full_stack_python.blog.public_detail import blog_public_detail_page
from full_stack_python.blog.page import blog_public_page
from full_stack_python.blog.state import BlogPublicState, BlogViewState, BlogPostState
from rxconfig import config

from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page
from .auth.state import SessionState

# --- ✨ CAMBIOS EN IMPORTS ✨ ---
# Importamos las páginas de gestión que acabamos de limpiar.
from .articles.list import manage_blog_posts_page
from .articles.detail import article_management_detail_page

# Importamos los paquetes completos para usar la notación paquete.componente
from . import blog, contact, navigation, pages

def index() -> rx.Component:
    """La página principal que redirige al dashboard si el usuario está autenticado."""
    return base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    ),
)

# --- Registro de Páginas ---

app.add_page(index)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# --- ✨ RUTAS DE ARTÍCULOS CORREGIDAS Y POTENCIADAS ✨ ---
# La ruta de artículos ahora apunta a la página de GESTIÓN de blog.
app.add_page(
    manage_blog_posts_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=BlogPostState.load_posts,
)

# La ruta de detalle ahora usa un parámetro consistente y carga los datos correctos.
# Asegúrate de que tu `BlogPostState.get_post_detail` use "blog_id"
app.add_page(
    article_management_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[blog_id]", 
    on_load=BlogPostState.get_post_detail,
)

# --- Rutas de Blog (privadas y públicas) ---
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=BlogPostState.load_posts
)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=BlogPostState.get_post_detail 
)

# Página de la galería pública
app.add_page(
    blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE,
    title="Galería pública",
    on_load=BlogPublicState.on_load
)
app.add_page(
    blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]",
    title="Detalle de la Publicación",
    on_load=BlogViewState.on_load
)

# --- Páginas de Contacto ---
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.load_entries
)