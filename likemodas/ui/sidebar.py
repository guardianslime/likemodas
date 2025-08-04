# likemodas/ui/sidebar.py (VERSIÓN RESPONSIVA COMPLETA)

import reflex as rx
from reflex.style import toggle_color_mode

from likemodas.ui.sidebar_items import sidebar_dark_mode_toggle_item
from reflex.style import toggle_color_mode
from..auth.state import SessionState
from.. import navigation

def sidebar_dark_mode_toggle_item() -> rx.Component:
    """Un componente que muestra un botón para alternar el modo de color."""
    return rx.button(
        rx.color_mode_cond(
            light=rx.icon(tag="sun"),
            dark=rx.icon(tag="moon")
        ),
        on_click=toggle_color_mode,
        variant="ghost"
    )

def sidebar_user_item() -> rx.Component:
    """Muestra el avatar y el nombre de usuario autenticado."""
    username = rx.cond(
        SessionState.authenticated_username,
        SessionState.authenticated_username,
        "Account"
    )
    return rx.cond(
        SessionState.is_authenticated,
        rx.hstack(
            rx.avatar(fallback=username, size="2"),
            rx.text(username, size="3", weight="medium"),
            align="center",
            spacing="3",
        ),
        rx.text("Account", size="3", weight="medium")
    )

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            rx.spacer(),
            rx.cond(
                has_notification,
                rx.box(
                    width="8px",
                    height="8px",
                    bg="red",
                    border_radius="50%",
                )
            ),
            width="100%", padding_x="0.5rem", padding_y="0.75rem", align="center",
            style={"_hover": {"bg": rx.color("accent", 4), "color": rx.color("accent", 11),}, "border-radius": "0.5em",},
        ),
        href=href, underline="none", weight="medium", width="100%",
    )

def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Dashboard", "layout-dashboard", navigation.routes.HOME_ROUTE),
        rx.cond(
            SessionState.is_admin,
            rx.fragment(
                sidebar_item("Blog", "newspaper", navigation.routes.BLOG_POSTS_ROUTE),
                sidebar_item("Create post", "square-library", navigation.routes.BLOG_POST_ADD_ROUTE),
                sidebar_item(
                    "Confirmar Pagos", 
                    "dollar-sign", 
                    "/admin/confirm-payments",
                    has_notification=SessionState.new_purchase_notification
                ),
                sidebar_item(
                    "Historial de Pagos",
                    "history",
                    "/admin/payment-history"
                )
            )
        ),
        sidebar_item("Contact", "mail", navigation.routes.CONTACT_US_ROUTE),
        sidebar_item("Contact History", "mailbox", navigation.routes.CONTACT_ENTRIES_ROUTE),
        spacing="1",
        width="100%",
    )

def sidebar_logout_item() -> rx.Component:
    """Un botón para cerrar la sesión del usuario."""
    return rx.cond(
        SessionState.is_authenticated,
        rx.button(
            "Logout",
            rx.icon(tag="log-out", margin_left="0.5em"),
            on_click=SessionState.do_logout,
            width="100%",
            variant="soft",
            color_scheme="red"
        )
    )

# --- ✨ NUEVO COMPONENTE: Menú de hamburguesa para Admin en móvil ---
def mobile_admin_menu() -> rx.Component:
    """
    Un menú desplegable (hamburguesa) que contiene los mismos enlaces 
    que la barra lateral, para ser usado en vistas móviles.
    """
    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                rx.button(rx.icon("menu", size=22), variant="ghost")
            ),
            rx.menu.content(
                rx.menu.item("Dashboard", on_click=rx.redirect(navigation.routes.HOME_ROUTE)),
                rx.menu.separator(),
                rx.menu.item("Blog", on_click=rx.redirect(navigation.routes.BLOG_POSTS_ROUTE)),
                rx.menu.item("Crear Post", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE)),
                rx.menu.item("Confirmar Pagos", on_click=rx.redirect("/admin/confirm-payments")),
                rx.menu.item("Historial de Pagos", on_click=rx.redirect("/admin/payment-history")),
                rx.menu.separator(),
                rx.menu.item("Contacto", on_click=rx.redirect(navigation.routes.CONTACT_US_ROUTE)),
                rx.menu.item("Historial de Contacto", on_click=rx.redirect(navigation.routes.CONTACT_ENTRIES_ROUTE)),
                rx.menu.separator(),
                rx.menu.item("Logout", on_click=SessionState.do_logout, color="red"),
            ),
        ),
        # Se muestra solo en móvil ('block') y se oculta en escritorio ('none')
        display=["block", "block", "none", "none", "none"],
    )

def sidebar() -> rx.Component:
    """
    Este componente ahora renderiza tanto la barra lateral para escritorio como 
    un menú de hamburguesa para móvil, usando estilos responsivos.
    """
    # Contenido de la barra lateral de escritorio
    desktop_sidebar_content = rx.vstack(
        rx.hstack(
            rx.image(
                src="/logo.png",
                width="9em",
                height="auto",
                border_radius="25%",
            ),
            align="center",
            justify="center",
            width="100%",
            margin_bottom="1.5em",
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
        spacing="5", padding_x="1em", padding_y="1.5em", bg="#2C004B",
        align="start", height="100vh",
    )

    return rx.fragment(
        # --- Barra lateral para Escritorio ---
        # Se oculta en móvil y se muestra en escritorio
        rx.box(
            desktop_sidebar_content,
            width="16em",
            display=["none", "none", "block", "block", "block"],
        ),
        # --- Menú para Móvil (se añade aquí para mantener la lógica junta) ---
        # Este menú se debe colocar en la parte superior de la vista móvil.
        # Lo incluimos aquí pero lo posicionaremos en `base_page.py`.
        mobile_admin_menu(),
    )