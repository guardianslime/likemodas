# likemodas/ui/sidebar.py (VERSIÓN CORREGIDA Y COMPLETA)

import reflex as rx
from reflex.style import toggle_color_mode
from..auth.state import SessionState
from.. import navigation

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
        # Fallback para estado no autenticado (aunque el sidebar no debería mostrarse)
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

def sidebar() -> rx.Component:
    # Contenido común para ambos layouts (escritorio y móvil)
    sidebar_content = rx.vstack(
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
        rx.box(
            sidebar_content,
            width="16em",
            display=["none", "none", "flex", "flex"], # Visible solo en md y superior
        ),
        # --- Cajón (Drawer) para Móvil ---
        rx.box(
            rx.drawer.root(
                rx.drawer.trigger(rx.icon("align-justify", size=30)), # Botón de menú
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(rx.drawer.close(rx.icon("x", size=30)), width="100%",),
                            # Reutiliza el mismo contenido de la barra lateral
                            sidebar_content,
                            width="100%",
                        ),
                        top="auto", right="auto", height="100%", width="20em", padding="1.5em", bg="#2C004B",
                    ),
                ),
                direction="left",
            ),
            padding="1em",
            display=["flex", "flex", "none", "none"], # Visible solo en base y sm
        )
    )