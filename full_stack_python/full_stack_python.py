"""Punto de entrada principal de la aplicación Reflex."""

import reflex as rx
import reflex_local_auth

from rxconfig import config
from .ui.base import base_page

# --- 1. Importaciones Organizadas ---
# Importaciones de módulos principales de la aplicación
from . import blog, contact, navigation, pages

# Importaciones específicas para la autenticación
from .auth.pages import (
    my_login_page,
    my_register_page,
)
from .auth.state import SessionState

# --- 2. Página Principal (Índice) ---
def index() -> rx.Component:
     """
     La página de inicio que se muestra de forma condicional.
     Muestra un dashboard si el usuario está autenticado, o una página de bienvenida si no lo está.
     """
     # NOTA: ArticlePublicState ya no existe, usamos el dashboard o la bienvenida.
     # Si quieres mostrar posts públicos en la página de inicio, necesitarás crear esa lógica en el 'blog.state'.
     return base_page(
          rx.cond(
               SessionState.is_authenticated,
               pages.dashboard_component(),
               pages.landing_component(),
          )
     )

# --- 3. Inicialización de la App ---
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

# Añadimos una ruta de "health check" para servicios como Railway.
@app.api.get("/healthz")
def healthz():
    return {"status": "OK"}

# --- 4. Registro de Páginas (Routes) ---

# Página de inicio
app.add_page(index)

# Páginas de Autenticación de reflex_local_auth
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
# La página de logout se maneja a través de un evento, no necesita una página completa.

# Páginas Generales de la Aplicación
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.list_entries
)

# --- CORRECCIÓN: Rutas del Blog Unificadas ---
# Todas las referencias a 'articles' han sido eliminadas.
# Ahora todo apunta al módulo 'blog' y a 'blog.BlogPostState'.

# Página que lista los posts del blog del usuario logueado.
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts
)

# Página para añadir un nuevo post.
app.add_page(
     blog.blog_post_add_page,
     route=navigation.routes.BLOG_POST_ADD_ROUTE,
)

# Página para ver los detalles de un post específico.
# El on_load ya está definido en el decorador @rx.page dentro de detail.py
app.add_page(blog.blog_post_detail_page)

# Página para editar un post existente.
# El on_load es necesario aquí para cargar los datos del post antes de mostrar el formulario.
app.add_page(
     blog.blog_post_edit_page,
     route="/blog/[blog_id]/edit",
     on_load=blog.BlogEditFormState.get_post_detail
)
