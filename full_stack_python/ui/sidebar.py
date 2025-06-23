# =================================================================
# ARCHIVO: full_stack_python/ui/sidebar.py (VERSIÓN CORREGIDA FINAL)
# Reemplaza todo el contenido de tu archivo con este bloque.
# =================================================================
import reflex as rx
from reflex.style import toggle_color_mode
import reflex_local_auth  # ¡CORRECCIÓN! Importamos la librería que contiene la ruta de login.

from ..auth.state import SessionState
from .. import navigation

def sidebar_user_item() -> rx.Component:
    """
    Muestra la información del usuario si está autenticado.
    De lo contrario, muestra un botón para iniciar sesión.
    """
    return rx.cond(
        SessionState.is_authenticated,
        # --- Si el usuario ESTÁ autenticado, muestra esto ---
        rx.hstack(
            rx.icon_button(
                rx.icon("user"),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.box(
                    rx.text(
                        SessionState.authenticated_username,
                        size="3",
                        weight="bold",
                    ),
                    rx.text(
                        rx.cond(
                            SessionState.authenticated_user_info,
                            SessionState.authenticated_user_info.email,
                            "Cargando email..."
                        ),
                        size="2",
                        weight="medium",
                    ),
                    width="100%",
                ),
                spacing="0",
                align="start",
                justify="start",
                width="100%",
            ),
            padding_x="0.5rem",
            align="center",
            justify="start",
            width="100%",
        ),
        # --- Si el usuario NO ESTÁ autenticado, muestra esto ---
        rx.link(
             rx.hstack(
                rx.icon_button(
                    rx.icon("log-in"),
                    size="3",
                    radius="full",
                ),
                rx.text("Login / Register", size="3", weight="bold"),
                align="center",
             ),
             # ¡CORRECCIÓN! Usamos la ruta correcta desde reflex_local_auth.
             href=reflex_local_auth.routes.LOGIN_ROUTE,
             width="100%",
        )
    )

def sidebar_logout_item() -> rx.Component:
    """Botón para cerrar sesión, solo se muestra si el usuario está autenticado."""
    return rx.cond(
        SessionState.is_authenticated,
        rx.box(
            rx.hstack(
                rx.icon("log-out"),
                rx.text("Logout", size="4"),
                width="100%",
                padding_x="0.5rem",
                padding_y="0.75rem",
                align="center",
                style={
                    "_hover": {
                        "cursor": "pointer",
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border-radius": "0.5em",
                },
            ),
            on_click=SessionState.perform_logout,
            as_='button',
            underline="none",
            weight="medium",
            width="100%",
        )
    )

def sidebar_dark_mode_toggle_item() -> rx.Component:
    """Botón para cambiar el modo oscuro/claro."""
    return rx.box(
        rx.hstack(
            rx.color_mode_cond(
                light=rx.icon("moon"),
                dark=rx.icon("sun"),
            ),
            rx.text(rx.color_mode_cond(
                light=("Turn dark mode on"),
                dark=("Turn light mode on"),
            ), size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "cursor": "pointer",
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "color": rx.color("accent", 11),
                "border-radius": "0.5em",
            },
        ),
        on_click=toggle_color_mode,
        as_='button',
        underline="none",
        weight="medium",
        width="100%",
    )

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    """Un item de menú genérico para el sidebar."""
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )

def sidebar_items() -> rx.Component:
    """Lista de todos los items del menú principal."""
    return rx.vstack(
        sidebar_item("Dashboard", "layout-dashboard", navigation.routes.HOME_ROUTE),
        sidebar_item("Articles", "globe", navigation.routes.ARTICLE_LIST_ROUTE),
        sidebar_item("Blog", "newspaper", navigation.routes.BLOG_POSTS_ROUTE),
        sidebar_item("Create post", "square-library", navigation.routes.BLOG_POST_ADD_ROUTE),
        sidebar_item("Contact", "mail", navigation.routes.CONTACT_US_ROUTE),
        sidebar_item("Contact History", "mailbox", navigation.routes.CONTACT_ENTRIES_ROUTE),
        spacing="1",
        width="100%",
    )

def sidebar() -> rx.Component:
    """El componente completo del sidebar, para escritorio y móvil."""
    return rx.box(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    rx.image(
                        src="/logo.jpg",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading("Reflex", size="7", weight="bold"),
                    align="center", justify="start", padding_x="0.5rem", width="100%",
                ),
                sidebar_items(),
                rx.spacer(),
                rx.vstack(
                    rx.vstack(
                        sidebar_dark_mode_toggle_item(),
                        sidebar_logout_item(),
                        spacing="1", width="100%",
                    ),
                    rx.divider(),
                    sidebar_user_item(),
                    width="100%", spacing="5",
                ),
                spacing="5", padding_x="1em", padding_y="1.5em",
                bg=rx.color("accent", 3), align="start", height="100vh", width="16em",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                rx.drawer.root(
                    rx.drawer.trigger(rx.icon("align-justify", size=30)),
                    rx.drawer.overlay(z_index="5"),
                    rx.drawer.portal(
                        rx.drawer.content(
                            rx.vstack(
                                rx.box(rx.drawer.close(rx.icon("x", size=30)), width="100%"),
                                sidebar_items(),
                                rx.spacer(),
                                rx.vstack(
                                    rx.vstack(
                                        sidebar_dark_mode_toggle_item(),
                                        sidebar_logout_item(),
                                        width="100%", spacing="1",
                                    ),
                                    rx.divider(margin="0"),
                                    sidebar_user_item(),
                                    width="100%", spacing="5",
                                ),
                                spacing="5", width="100%",
                            ),
                            top="auto", right="auto", height="100%", width="20em",
                            padding="1.5em", bg=rx.color("accent", 2),
                        ),
                    ),
                    direction="left",
                ),
                padding="1em",
            )
        ),
    )
