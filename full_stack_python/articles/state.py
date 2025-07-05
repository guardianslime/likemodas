import reflex as rx
import reflex_local_auth
from rxconfig import config

# --- Módulos y Componentes ---
from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page
from .auth.state import SessionState

# --- ¡Importaciones directas y explícitas para todo! ---
from .articles.state import ArticlePublicState
from .articles.list import article_public_list_page
from .articles.detail import article_detail_page
from .blog.state import BlogPostState
from .blog.list import blog_post_list_page
from .blog.add import blog_post_add_page
from .blog.detail import blog_post_detail_page
from .blog.edit import blog_post_edit_page
from .contact.state import ContactState
from .contact.page import contact_page, contact_entries_list_page
from . import navigation, pages

def index() -> rx.Component:
    """La página principal que redirige al dashboard."""
    return base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, panel_background="solid",
        scaling="90%", radius="medium", accent_color="sky"
    )
)

# --- Registro de Páginas (usando on_mount en cada página) ---
app.add_page(index)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/")
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# Páginas de Artículos
app.add_page(article_public_list_page, route=navigation.routes.ARTICLE_LIST_ROUTE)
app.add_page(article_detail_page, route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]")

# Páginas de Blog
app.add_page(blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE)
app.add_page(blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog_post_detail_page, route="/blog/[blog_id]")
app.add_page(blog_post_edit_page, route="/blog/[blog_id]/edit")

# Páginas de Contacto
app.add_page(contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=ContactState.load_entries)