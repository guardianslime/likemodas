# likemodas/ui/nav.py (SOLUCIÓN MANUAL Y DEFINITIVA PARA 0.7.0)

import reflex as rx
from .. import navigation
from ..state import AppState

def notification_icon() -> rx.Component:
    """Componente de notificaciones construido manualmente para máxima compatibilidad."""
    icon_color = rx.color_mode_cond("black", "white")

    # El menú desplegable como un Vstack que se muestra/oculta con rx.cond
    notifications_dropdown = rx.vstack(
        rx.cond(
            AppState.notifications,
            rx.foreach(
                AppState.notifications,
                lambda n: rx.button(
                    rx.box(
                        rx.text(n.message, weight=rx.cond(n.is_read, "normal", "bold")),
                        rx.text(n.created_at_formatted, font_size="0.8em", color_scheme="gray"),
                        text_align="left",
                    ),
                    on_click=[
                        rx.cond(n.url, rx.redirect(n.url), rx.toast.info("Esta notificación no tiene un enlace.")),
                        AppState.toggle_notifications, # Cierra el menú al hacer clic
                    ],
                    variant="ghost",
                    width="100%",
                    padding_y="0.5em",
                    height="auto",
                )
            ),
            rx.text("No tienes notificaciones.", padding="1em")
        ),
        # Estilos para que aparezca como un menú flotante
        position="absolute",
        top="120%", # Un poco debajo del icono
        right="0",
        bg=rx.color_mode_cond("white", "#2C004B"),
        border="1px solid #ededed",
        border_radius="md",
        box_shadow="lg",
        z_index="1000",
        width="300px",
        spacing="0",
        max_height="300px",
        overflow_y="auto",
    )

    # El contenedor principal
    return rx.box(
        # El icono de la campana que actúa como botón
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
            on_click=[AppState.mark_all_as_read, AppState.toggle_notifications]
        ),
        # El menú desplegable que se muestra condicionalmente
        rx.cond(
            AppState.show_notifications,
            notifications_dropdown
        ),
        position="relative" # Clave para que el menú se posicione correctamente
    )


def public_navbar() -> rx.Component:
    """La barra de navegación pública."""
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