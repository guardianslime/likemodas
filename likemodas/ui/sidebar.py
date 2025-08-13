# likemodas/ui/sidebar.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .. import navigation

# Las funciones internas como sidebar_item, etc., no necesitan cambios.
# Las incluyo para que puedas reemplazar el archivo completo.

def sidebar_dark_mode_toggle_item() -> rx.Component:
    return rx.button(
        rx.color_mode_cond(light=rx.icon(tag="sun"), dark=rx.icon(tag="moon")),
        on_click=toggle_color_mode,
        variant="ghost"
    )

def sidebar_user_item() -> rx.Component:
    return rx.cond(
        AppState.is_authenticated,
        rx.hstack(
            rx.avatar(fallback=AppState.authenticated_user.username[0].upper(), size="2"),
            rx.text(AppState.authenticated_user.username, size="3", weight="medium"),
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
                rx.box(width="8px", height="8px", bg="red", border_radius="50%")
            ),
            width="100%", padding_x="0.5rem", padding_y="0.75rem", align="center",
            style={"_hover": {"bg": rx.color("accent", 4), "color": rx.color("accent", 11)}, "border-radius": "0.5em"},
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
        on_click=lambda: AppState.set_show_admin_sidebar(False),
    )

def sidebar_items() -> rx.Component:
    return rx.vstack(
        rx.cond(
            AppState.is_admin,
            rx.fragment(
                rx.vstack(
                    sidebar_item("Dashboard", "users", "/admin/users"),
                    sidebar_item("Mis Publicaciones", "newspaper", "/blog"),
                    sidebar_item("Crear Publicación", "square-plus", navigation.routes.BLOG_POST_ADD_ROUTE),
                    sidebar_item("Confirmar Pagos", "dollar-sign", "/admin/confirm-payments", has_notification=AppState.new_purchase_notification),
                    sidebar_item("Historial de Pagos", "history", "/admin/payment-history"),
                    sidebar_item("Mensajes de Contacto", "mailbox", navigation.routes.CONTACT_ENTRIES_ROUTE),
                    spacing="1", width="100%"
                ),
                rx.divider(margin_y="1em"),
            )
        ),
        sidebar_item("Tienda", "store", "/admin/store"),
        sidebar_item("Contacto", "mail", navigation.routes.CONTACT_US_ROUTE),
        spacing="1", width="100%",
    )

def sidebar_logout_item() -> rx.Component:
    return rx.cond(
        AppState.is_authenticated,
        rx.button(
            "Logout", rx.icon(tag="log-out", margin_left="0.5em"),
            on_click=AppState.do_logout,
            width="100%", variant="soft", color_scheme="red"
        )
    )

def sliding_admin_sidebar() -> rx.Component:
    """
    El componente principal del sidebar con la posición y altura corregidas.
    """
    SIDEBAR_WIDTH = "16em"

    sidebar_panel = rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom="1.5em",
        ),
        sidebar_items(),
        rx.spacer(),
        rx.vstack(
            rx.vstack(sidebar_dark_mode_toggle_item(), sidebar_logout_item(), spacing="1", width="100%"),
            rx.divider(),
            sidebar_user_item(),
            width="100%", spacing="5",
        ),
        spacing="5", padding_x="1em", padding_y="1.5em", bg="#2C004B",
        align="start", height="100%", width=SIDEBAR_WIDTH,
    )

    return rx.box(
        rx.hstack(
            sidebar_panel,
            rx.box(
                rx.text(
                    "LIKEMODAS",
                    style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.2em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}
                ),
                on_click=AppState.toggle_admin_sidebar,
                cursor="pointer",
                bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0",
                height="150px",
                display="flex",
                align_items="center"
            ),
            align_items="center",
            spacing="0",
        ),
        # --- CORRECCIONES CLAVE DE POSICIÓN ---
        position="fixed",
        top="0",                 # Anclarlo a la parte superior
        left="0",                # Anclarlo a la izquierda
        height="100vh",          # Ocupar el 100% de la altura de la ventana
        display="flex",          # Usar flexbox para centrar verticalmente
        align_items="center",    # Centrar el hstack (panel + botón) verticalmente
        transform=rx.cond(
            AppState.show_admin_sidebar,
            "translateX(0)",
            f"translateX(-{SIDEBAR_WIDTH})"
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )
