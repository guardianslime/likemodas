# likemodas/ui/nav.py

import reflex as rx
from .search_state import SearchState
from ..cart.state import CartState
from ..auth.state import SessionState
from ..notifications.state import NotificationState
# Se importa AppState para acceder a los métodos de navegación heredados
from ..state import AppState

def notification_icon() -> rx.Component:
    """Icono de notificaciones con contador."""
    icon_color = rx.color_mode_cond("black", "white")
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("bell", size=28, color=icon_color),
                rx.cond(
                    NotificationState.unread_count > 0,
                    rx.box(
                        rx.text(NotificationState.unread_count, size="1", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full",
                        bg="red", color="white",
                    )
                ),
                position="relative",
                padding="0.5em",
                cursor="pointer"
            ),
        ),
        rx.menu.content(
            rx.cond(
                NotificationState.notifications,
                rx.foreach(
                    NotificationState.notifications,
                    lambda n: rx.menu.item(
                        rx.box(
                            rx.text(n.message, weight=rx.cond(n.is_read, "regular", "bold")),
                            rx.text(n.created_at_formatted, size="2", color_scheme="gray"),
                        ),
                        on_click=rx.cond(
                            n.url,
                            rx.redirect(n.url),
                            rx.toast.info("Esta notificación no tiene un enlace.")
                        )
                    )
                ),
                rx.menu.item("No tienes notificaciones.")
            ),
            bg="#2C004BF0",
            style={"backdrop_filter": "blur(10px)"},
            max_height="300px",
            overflow_y="auto"
        ),
        on_open_change=lambda open: rx.cond(open, NotificationState.mark_all_as_read, None)
    )

def public_navbar() -> rx.Component:
    """Barra de navegación pública, rediseñada para ser robusta y responsiva."""
    icon_color = rx.color_mode_cond("black", "white")
    
    return rx.box(
        rx.grid(
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=22, color=icon_color), variant="ghost")
                    ),
                    rx.menu.content(
                        # Las llamadas ahora apuntan directamente a AppState
                        rx.menu.item("Home", on_click=AppState.to_home),
                        rx.menu.sub(
                            rx.menu.sub_trigger("Categorías"),
                            rx.menu.sub_content(
                                rx.menu.item("Ropa", on_click=rx.redirect("/category/ropa")),
                                rx.menu.item("Calzado", on_click=rx.redirect("/category/calzado")),
                                rx.menu.item("Mochilas", on_click=rx.redirect("/category/mochilas")),
                                rx.menu.separator(),
                                rx.menu.item("Ver Todo", on_click=rx.redirect("/")),
                            ),
                        ),
                        rx.menu.item("Contact", on_click=AppState.to_contact),
                        rx.menu.separator(),
                        rx.cond(
                            SessionState.is_authenticated,
                            rx.fragment(
                                rx.menu.item("Mi Cuenta", on_click=AppState.to_my_account),
                                rx.menu.item("Logout", on_click=AppState.to_logout),
                            ),
                            rx.fragment(
                                rx.menu.item("Login", on_click=AppState.to_login),
                                rx.menu.item("Register", on_click=AppState.to_register),
                            )
                        ),
                        bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
                    ),
                ),
                rx.image(src="/logo.png", width="8em", height="auto", border_radius="md"),
                align="center", spacing="4", justify="start",
            ),
            
            rx.form(
                rx.input(
                    placeholder="Buscar productos...",
                    value=SearchState.search_term,
                    on_change=SearchState.set_search_term,
                    width="100%",
                ),
                on_submit=SearchState.perform_search,
                width="100%",
            ),
            
            rx.hstack(
                rx.cond(
                    SessionState.is_authenticated,
                    rx.fragment(
                        notification_icon(),
                        rx.link(
                            rx.box(
                                rx.icon("shopping-cart", size=22, color=icon_color),
                                rx.cond(
                                    CartState.cart_items_count > 0,
                                    rx.box(
                                        rx.text(CartState.cart_items_count, size="1", weight="bold"),
                                        position="absolute", top="-5px", right="-5px",
                                        padding="0 0.4em", border_radius="full",
                                        bg="red", color="white",
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
  
            columns="auto 1fr auto",
            align_items="center",
            width="100%",
            gap="1.5rem",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
        on_mount=[
            NotificationState.load_notifications,
        ],
    )