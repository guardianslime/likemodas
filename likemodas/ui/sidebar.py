# likemodas/ui/sidebar.py (CORREGIDO Y RESPONSIVO)

import reflex as rx
from ..state import AppState
from .. import navigation

# La constante para el ancho del sidebar
SIDEBAR_WIDTH = "16em"

def sidebar_item(text: str, icon: str, href: str, has_notification: rx.Var[bool] = None) -> rx.Component:
    """Componente de enlace de sidebar que resalta la página activa."""
    is_active = (AppState.current_path == href)
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            rx.spacer(),
            rx.cond(
                has_notification,
                rx.box(width="8px", height="8px", bg="red", border_radius="50%")
            ),
            bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
            color=rx.cond(is_active, rx.color("violet", 11), rx.color_mode_cond("black", "white")),
            font_weight=rx.cond(is_active, "bold", "normal"),
            border_radius="var(--radius-3)",
            width="100%",
            padding="0.75em",
            align="center",
            _hover={
                "background_color": rx.color("violet", 5),
            },
        ),
        href=href,
        underline="none",
        width="100%",
    )

def sidebar_items_content() -> rx.Component:
    """El contenido interno del sidebar (los enlaces y la sección de usuario)."""
    return rx.vstack(
        rx.hstack(
            rx.image(src="/logo.png", width="9em", height="auto", border_radius="25%"),
            align="center", justify="center", width="100%", margin_bottom="1.5em",
        ),
        rx.vstack(
            rx.cond(
                AppState.is_admin,
                rx.fragment(
                    rx.vstack(
                        sidebar_item("Dashboard", "layout-dashboard", "/admin/users"),
                        sidebar_item("Mis Publicaciones", "newspaper", "/blog"),
                        sidebar_item("Crear Publicación", "square-plus", navigation.routes.BLOG_POST_ADD_ROUTE),
                        sidebar_item("Mi Ubicación de Envío", "map-pin", "/admin/my-location"),
                        sidebar_item("Confirmar Pagos", "dollar-sign", "/admin/confirm-payments", has_notification=AppState.new_purchase_notification),
                        sidebar_item("Historial de Pagos", "history", "/admin/payment-history"),
                        sidebar_item("Solicitudes de Soporte", "mailbox", navigation.routes.SUPPORT_TICKETS_ROUTE),
                        spacing="2",
                        width="100%"
                    ),
                    rx.divider(margin_y="1em"),
                )
            ),
            sidebar_item("Tienda", "store", "/admin/store"),
            spacing="2",
            width="100%",
        ),
        rx.spacer(),
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.cond(
                    AppState.is_authenticated,
                    rx.hstack(
                        rx.avatar(fallback=AppState.authenticated_user.username[0].upper(), size="2"),
                        rx.text(AppState.authenticated_user.username, size="3", weight="medium"),
                        align="center",
                        spacing="3",
                    ),
                ),
                rx.spacer(), width="100%", justify="between",
            ),
            rx.cond(
                AppState.is_authenticated,
                rx.button(
                    "Logout",
                    rx.icon(tag="log-out", margin_left="0.5em"),
                    on_click=AppState.do_logout,
                    width="100%",
                    variant="soft",
                    color_scheme="red"
                )
            ),
            width="100%", spacing="3",
        ),
        spacing="5", padding="1em",
        align="start", height="100vh",
    )

def admin_sidebar() -> rx.Component:
    """El sidebar fijo para la vista de escritorio."""
    return rx.box(
        sidebar_items_content(),
        display=["none", "none", "block"],
        position="fixed",
        left="0",
        top="0",
        height="100%",
        width=SIDEBAR_WIDTH,
        z_index="999",
        bg=rx.color("gray", 2),
    )

def admin_mobile_sidebar() -> rx.Component:
    """El menú de hamburguesa y el cajón deslizable para la vista móvil."""
    return rx.box(
        rx.drawer.root(
            rx.drawer.trigger(
                rx.icon_button(
                    rx.icon("menu", size=24),
                    variant="ghost",
                    color_scheme="gray",
                )
            ),
            rx.drawer.content(
                sidebar_items_content(),
                top="auto",
                right="auto",
                height="100%",
                width=SIDEBAR_WIDTH,
                padding="1em",
                bg=rx.color("gray", 2),
            ),
            direction="left",
            open=AppState.show_admin_sidebar,
            on_open_change=AppState.set_show_admin_sidebar,
        ),
        display=["block", "block", "none"],
        position="fixed",
        top="0.5rem",
        left="0.5rem",
        z_index="1000",
    )