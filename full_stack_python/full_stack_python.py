"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import reflex_local_auth
from rxconfig import config

# --- Módulos y Componentes ---
from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page
from .auth.state import SessionState

# Se importan los paquetes completos para usar la notación paquete.componente
from . import contact, navigation, pages

# --- NUEVO: IMPORTAR SOLO EL MÓDULO DE PÁGINAS DEL BLOG ---
from .blog import page as blog_pages


# --- Definición de la Aplicación ---
def index() -> rx.Component:
    """La página principal que redirige al dashboard si el usuario está autenticado."""
    # Esta parte se puede quedar igual si quieres mantener la autenticación para otras partes.
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
    )
)

# --- Registro de Páginas ---

app.add_page(index)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# --- RUTAS DEL BLOG SIMPLIFICADAS ---
# (Elimina todas las rutas anteriores del blog)
app.add_page(blog_pages.blog_list_page, route="/blog")
app.add_page(blog_pages.blog_add_page, route="/blog/add")

# Páginas de Contacto (las puedes dejar si las usas)
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.load_entries
)