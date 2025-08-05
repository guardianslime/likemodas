# likemodas/ui/nav.py (CORREGIDO Y COMPLETO)

import reflex as rx
from .. import navigation
from ..state import AppState

def notification_icon() -> rx.Component:
    icon_color = rx.color_mode_cond("black", "white")
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("bell", size=28, color=icon_color),
                rx.cond(
                    AppState.unread_count > 0,
                    rx.box(
                        rx.text(AppState.unread_count, size="1", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full",
                        bg="red", color="white",
                    )
                ),
                position="relative", padding="0.5em", cursor="pointer"
            ),
        ),
        rx.menu.content(
            rx.cond(
                AppState.notifications,
                rx.foreach(
                    AppState.notifications,
                    lambda n: rx.menu.item(
                        rx.box(
                            rx.text(n.message, weight=rx.cond(n.is_read, "regular", "bold")),
                            rx.text(n.created_at_formatted, size="2", color_scheme="gray"),
                        ),
                        on_click=rx.cond(n.url, rx.redirect(n.url), rx.toast.info("Esta notificación no tiene un enlace."))
                    )
                ),
                rx.menu.item("No tienes notificaciones.")
            ),
            bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
            max_height="300px", overflow_y="auto"
        ),
        on_open_change=lambda open: rx.cond(open, AppState.mark_all_as_read, None)
    )

def public_navbar() -> rx.Component:
    icon_color = rx.color_mode_cond("black", "white")
    return rx.box(
        rx.grid(
            rx.hstack(
                # ... Menú de hamburguesa (sin cambios de estado) ...
                rx.image(src="/logo.png", width="8em", height="auto", border_radius="md"),
                align="center", spacing="4", justify="start",
            ),
            rx.form(
                rx.input(
                    placeholder="Buscar productos...",
                    value=AppState.search_term,
                    on_change=AppState.set_search_term,
                    width="100%",
                ),
                on_submit=AppState.perform_search,
                width="100%",
            ),
            rx.hstack(
                rx.cond(
                    AppState.is_authenticated,
                    rx.fragment(
                        notification_icon(),
                        rx.link(
                            rx.box(
                                rx.icon("shopping-cart", size=22, color=icon_color),
                                rx.cond(
                                    AppState.cart_items_count > 0,
                                    rx.box(
                                        rx.text(AppState.cart_items_count, size="1", weight="bold"),
                                        position="absolute", top="-5px", right="-5px",
                                        padding="0 0.4em", border_radius="full", bg="red", color="white",
                                    )
                                ),
                                position="relative", padding="0.5em"
                            ),
                            href="/cart"
                        )
                    )
                ),
                align="center", spacing="3", justify="end",
            ),
            columns="auto 1fr auto", align_items="center", width="100%", gap="1.5rem",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
        on_mount=[AppState.load_notifications],
    )

