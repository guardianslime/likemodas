# likemodas/ui/nav.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from .. import navigation
from ..state import AppState
from ..models import Category

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
                AppState.user_notifications,
                rx.menu.item(
                    rx.hstack(
                        rx.icon("trash_2", size=16),
                        rx.text("Limpiar todo")
                    ),
                    # --- ✨ CORRECCIÓN 1: Se llama a la nueva función de borrado ---
                    on_click=AppState.clear_all_notifications,
                    color_scheme="red",
                ),
            ),
            rx.divider(margin_y="0.5em"),
            rx.cond(
                AppState.user_notifications,
                rx.foreach(
                    AppState.user_notifications,
                    lambda n: rx.menu.item(
                        # --- ✨ CORRECCIÓN 2: Nuevo diseño para cada notificación ---
                        rx.vstack(
                            rx.text(
                                n.message,
                                weight=rx.cond(n.is_read, "regular", "bold"),
                                white_space="normal", # Permite que el texto se ajuste
                                width="100%",
                                size="3"
                            ),
                            rx.hstack(
                                rx.spacer(), # Empuja la fecha hacia la derecha
                                rx.text(
                                    n.created_at_formatted,
                                    size="2",
                                    color_scheme="gray",
                                    margin_top="0.5em"
                                ),
                                width="100%"
                            ),
                            align_items="start", # Alinea el contenido a la izquierda
                            spacing="1",
                            padding="0.5em 0.75em",
                            bg=rx.cond(n.is_read, "transparent", rx.color("violet", 3)),
                            border_radius="md",
                            width="100%",
                        ),
                        # --- Fin del nuevo diseño ---
                        on_click=rx.cond(n.url, rx.redirect(n.url), AppState.do_nothing),
                        padding="0.25em",
                    )
                ),
                rx.menu.item("No tienes notificaciones.")
            ),
            bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
            max_height="400px", overflow_y="auto",
            min_width="350px", # Aumentamos el ancho para más espacio
        ),
        on_open_change=lambda open: rx.cond(open, None, AppState.mark_all_as_read)
    )


def public_navbar() -> rx.Component:
    """La barra de navegación pública definitiva, con menú de hamburguesa."""
    icon_color = rx.color_mode_cond("black", "white")
    
    hamburger_menu = rx.menu.root(
        # ... (este componente no cambia)
        rx.menu.trigger(
            rx.icon("menu", size=28, cursor="pointer", color=icon_color)
        ),
        rx.menu.content(
            rx.menu.item("Inicio", on_click=lambda: rx.redirect("/")),
            rx.menu.sub(
                rx.menu.sub_trigger("Categorías"),
                rx.menu.sub_content(
                    rx.menu.item("Ropa", on_click=lambda: rx.redirect(f"/?category={Category.ROPA.value}")),
                    rx.menu.item("Calzado", on_click=lambda: rx.redirect(f"/?category={Category.CALZADO.value}")),
                    rx.menu.item("Mochilas", on_click=lambda: rx.redirect(f"/?category={Category.MOCHILAS.value}")),
                    rx.menu.item("Ver Todo", on_click=lambda: rx.redirect("/")),
                ),
            ),
            rx.menu.separator(),
            rx.menu.item("Mi Cuenta", on_click=lambda: rx.redirect("/my-account/shipping-info")),
            rx.menu.item("Mis Compras", on_click=lambda: rx.redirect("/my-purchases")),
        ),
    )

    authenticated_icons = rx.hstack(
        # ... (este componente no cambia)
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
        ),
        align="center",
        spacing="3",
        justify="end",
    )
    
    placeholder_icons = rx.hstack(
        # ... (este componente no cambia)
        rx.box(width="44px", height="44px", padding="0.5em"),
        rx.box(width="38px", height="44px", padding="0.5em"),
        align="center",
        spacing="3",
        justify="end",
    )

    return rx.box(
        # La parte visible de la barra de navegación
        rx.grid(
            # ... (el grid con el logo, buscador, etc., no cambia)
            rx.hstack(
                hamburger_menu,
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
            columns="auto 1fr auto",
            align_items="center",
            width="100%",
            gap="1.5rem",
        ),
        
        # --- ✨ INICIO: SOLUCIÓN CON BOTÓN OCULTO ✨ ---
        # 1. Un botón estándar de Reflex, completamente oculto, que solo existe
        #    si el usuario ha iniciado sesión.
        rx.cond(
            AppState.is_authenticated,
            rx.button(
                "Polling Trigger", # El texto no importa
                on_click=AppState.poll_notifications,
                id="notification_poller_button", # ID único para que JS lo encuentre
                display="none", # Lo oculta completamente
            ),
        ),

        # 2. El script que "pulsa" el botón invisible cada 15 segundos.
        #    También solo se activa si el usuario ha iniciado sesión.
        # --- ✨ INICIO: SOLUCIÓN DE POLLING ROBUSTA ✨ ---
        rx.cond(
            AppState.is_authenticated,
            rx.fragment(
                # 1. Un botón de Reflex, completamente oculto.
                rx.button(
                    "Polling Trigger",
                    on_click=AppState.poll_notifications,
                    id="notification_poller_button",
                    display="none",
                ),

                # 2. El script que "pulsa" el botón invisible cada 15 segundos.
                #    Este script solo se renderizará si el usuario está autenticado.
                rx.box(
                    on_mount=rx.call_script(
                        """
                        if (!window.likemodas_notification_poller) {
                            window.likemodas_notification_poller = setInterval(() => {
                                const trigger = document.getElementById('notification_poller_button');
                                if (trigger) {
                                    trigger.click();
                                }
                            }, 15000);
                        }
                        """
                    ),
                    display="none",
                )
            )
        ),
        # --- ✨ FIN: SOLUCIÓN DE POLLING ROBUSTA ✨ ---

        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", 
        style={"backdrop_filter": "blur(10px)"},
        on_mount=[AppState.load_notifications],
    )