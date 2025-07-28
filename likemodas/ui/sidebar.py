# likemodas/ui/sidebar.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
from reflex.style import toggle_color_mode

from ..auth.state import SessionState # ✅ Se importa SessionState, que es seguro.
from .. import navigation
from ..models import UserRole
# ❗️ Se elimina cualquier importación de AdminConfirmState.

# ... (las funciones sidebar_user_item, sidebar_logout_item, etc. no cambian) ...
def sidebar_user_item() -> rx.Component:
    user_info_obj = SessionState.authenticated_user_info
    username_via_user_abj = rx.cond(SessionState.authenticated_username, SessionState.authenticated_username, "Account")
    return rx.cond(
       user_info_obj,
        rx.hstack(
            rx.icon_button(rx.icon("user"), size="3", radius="full",),
            rx.vstack(
                rx.box(
                    rx.text(username_via_user_abj, size="3", weight="bold",),
                    rx.text(f"{user_info_obj.email}", size="2", weight="medium",),
                    width="100%",
                ),
                spacing="0", align="start", justify="start", width="100%",
            ),
            padding_x="0.5rem", align="center", justify="start", width="100%",
        ),
        rx.fragment("")
    )

def sidebar_logout_item() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("log-out"), rx.text("Logout", size="4"),
            width="100%", padding_x="0.5rem", padding_y="0.75rem", align="center",
            style={"_hover": {"cursor": "pointer", "bg": rx.color("accent", 4), "color": rx.color("accent", 11),}, "color": rx.color("accent", 11), "border-radius": "0.5em",},
        ),
        on_click=navigation.NavState.to_logout, as_='button', underline="none", weight="medium", width="100%",
    )

def sidebar_dark_mode_toggle_item() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.color_mode_cond(light=rx.icon("moon"), dark=rx.icon("sun"),),
            rx.text(rx.color_mode_cond(light=("Turn dark mode on"), dark=("Turn light mode on"),), size="4"),
            width="100%", padding_x="0.5rem", padding_y="0.75rem", align="center",
            style={"_hover": {"cursor": "pointer", "bg": rx.color("accent", 4), "color": rx.color("accent", 11),}, "color": rx.color("accent", 11), "border-radius": "0.5em",},
        ),
        on_click=toggle_color_mode, as_='button', underline="none", weight="medium", width="100%",
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
# ...

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
                    # ✅ CAMBIO: Ahora lee desde SessionState, que es seguro.
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
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.image(src="/logo.jpg", width="2.25em", height="auto", border_radius="25%",),
                rx.heading("Likemodas", size="7", weight="bold"),
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
            spacing="5", padding_x="1em", padding_y="1.5em", bg=rx.color("accent", 3),
            align="start", height="100vh", width="16em",
            display=["none", "none", "flex", "flex"],
        ),
        rx.drawer.root(
            rx.drawer.trigger(rx.icon("align-justify", size=30, display=["flex", "flex", "none", "none"])),
            rx.drawer.overlay(z_index="5"),
            rx.drawer.portal(
                rx.drawer.content(
                    rx.vstack(
                        rx.box(rx.drawer.close(rx.icon("x", size=30)), width="100%",),
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
                    top="auto", right="auto", height="100%", width="20em", padding="1.5em", bg=rx.color("accent", 2),
                ),
                width="100%",
            ),
            direction="left",
        ),
        padding="1em",
    )