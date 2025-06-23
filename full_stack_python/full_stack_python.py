# -----------------------------------------------------------------
# full_stack_python/full_stack_python.py (Archivo Principal - VERSIÓN CORREGIDA)
# -----------------------------------------------------------------

"""Punto de entrada principal de la aplicación Reflex."""

import reflex as rx
import sqlalchemy
import reflex_local_auth
from reflex_local_auth.user import LocalUser

from rxconfig import config
from .ui.base import base_page

from .auth.pages import (
    my_login_page,
    my_register_page,
    my_logout_page
)
from .auth.state import SessionState

from .articles.detail import article_detail_page
from .articles.list import article_public_list_page
from .articles.state import ArticlePublicState

from . import blog, contact, navigation, pages

def index() -> rx.Component:
    """Página de inicio que muestra el dashboard si está autenticado, o la landing page si no."""
    return base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

# Configuración principal de la aplicación Reflex
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )
)

# --- RUTA DE DIAGNÓSTICO DE LA BASE DE DATOS ---
# ¡IMPORTANTE! Esta es tu herramienta más valiosa para depurar.
@app.api.get("/db_healthz")
def db_healthz():
    """Verifica el estado de la conexión a la base de datos."""
    try:
        print("--- [db_healthz] Iniciando prueba de conexión a la BD. ---")
        with rx.session() as session:
            session.exec(sqlalchemy.text("SELECT 1"))
        print("--- [db_healthz] ¡Prueba de conexión a la BD EXITOSA! ---")
        return {"status": "OK", "message": "La conexión a la base de datos es exitosa."}
    except Exception as e:
        print(f"!!!!!!!!!! [db_healthz] PRUEBA DE CONEXIÓN FALLIDA: {e} !!!!!!!!!!!")
        return {"status": "ERROR", "detail": str(e)}, 500

# --- Definición de las páginas de la aplicación ---

app.add_page(index, on_load=ArticlePublicState.load_posts)

# Páginas de autenticación de reflex_local_auth
app.add_page(
    my_login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Login",
)
app.add_page(
    my_register_page,
    route=reflex_local_auth.routes.REGISTER_ROUTE,
    title="Register",
)
app.add_page(
    my_logout_page,
    route=navigation.routes.LOGOUT_ROUTE,
    title="Logout"
)

# Páginas personalizadas
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)

app.add_page(
    pages.protected_page,
    route="/protected/",
    on_load=SessionState.on_load
)

app.add_page(
    article_public_list_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=ArticlePublicState.load_posts
)

app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticlePublicState.get_post_detail
)

app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts
)

app.add_page(
    blog.blog_post_add_page,
    route=navigation.routes.BLOG_POST_ADD_ROUTE,
)

app.add_page(
    blog.blog_post_detail_page,
    route="/blog/[blog_id]",
    on_load=blog.BlogPostState.get_post_detail
)

app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=blog.BlogPostState.get_post_detail
)

app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.list_entries
)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)
