# likemodas/ui/nav.py (CORREGIDO Y COMPATIBLE CON REFLEX 0.7.0)

import reflex as rx
from .. import navigation
from ..state import AppState

def notification_icon() -> rx.Component:
    """Componente para el icono y menú de notificaciones con la sintaxis correcta para 0.7.0."""
    icon_color = rx.color_mode_cond("black", "white")
    
    # --- CAMBIO CLAVE ---
    # Se elimina `rx.menu_button`. El `rx.box` ahora es el primer hijo de `rx.menu`
    # y actúa como el botón que abre el menú.
    return rx.menu(
        rx.box(
            rx.icon("bell", size=28, color=icon_color),
            rx.cond(
                AppState.unread_count > 0,
                rx.box(
                    rx.text(AppState.unread_count, font_size="0.7em", weight="bold"),
                    position="absolute", top="-5px", right="-5px",
                    padding="0 0.4em", border_radius="full",
                    bg="red", color="white",
                )
            ),
            position="relative", 
            padding="0.5em", 
            cursor="pointer",
            # El evento para marcar como leídas se pone en el botón que abre el menú.
            on_click=AppState.mark_all_as_read
        ),
        # El rx.menu_list se mantiene igual.
        rx.menu_list(
            rx.cond(
                AppState.notifications,
                rx.foreach(
                    AppState.notifications,
                    lambda n: rx.menu_item(
                        rx.box(
                            rx.text(n.message, weight=rx.cond(n.is_read, "normal", "bold")),
                            rx.text(n.created_at_formatted, font_size="0.8em", color_scheme="gray"),
                        ),
                        on_click=rx.cond(n.url, rx.redirect(n.url), rx.toast.info("Esta notificación no tiene un enlace."))
                    )
                ),
                rx.menu_item("No tienes notificaciones.")
            ),
            max_height="300px", 
            overflow_y="auto"
        ),
    )

def public_navbar() -> rx.Component:
    """
    La barra de navegación pública. Este código ya era mayormente compatible,
    pero lo incluyo completo por consistencia.
    """
    icon_color = rx.color_mode_cond("black", "white")
    
    authenticated_icons = rx.hstack(
        notification_icon(),
        rx.link(
            rx.box(
                rx.icon("shopping-cart", size=22, color=icon_color),
                rx.cond(
                    AppState.cart_items_count > 0,
                    rx.box(
                        rx.text(AppState.cart_items_count, font_size="0.7em", weight="bold"),
                        position="absolute", top="-5px", right="-5px",
                        padding="0 0.4em", border_radius="full", bg="red", color="white",
                    )
                ),
                position="relative", padding="0.5em"
            ),
            href="/cart"
        ),
        align="center",
        spacing="3",
        justify="end",
    )
    
    placeholder_icons = rx.hstack(
        rx.box(width="44px", height="44px", padding="0.5em"),
        rx.box(width="38px", height="44px", padding="0.5em"),
        align="center",
        spacing="3",
        justify="end",
    )

    return rx.box(
        rx.grid(
            rx.hstack(
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
            
            rx.cond(
                AppState.is_authenticated,
                authenticated_icons,
                placeholder_icons
            ),

            template_columns="auto 1fr auto",
            align_items="center",
            width="100%",
            gap="1.5rem",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", 
        style={"backdrop_filter": "blur(10px)"},
        on_mount=[AppState.load_notifications],
    )