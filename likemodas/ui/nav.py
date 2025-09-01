import reflex as rx
from .. import navigation
from ..state import AppState
from ..models import Category

def notification_icon() -> rx.Component:
    """Componente para el icono y menú de notificaciones."""
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
            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Ahora itera sobre una lista de DTOs, que es seguro.
            rx.cond(
                AppState.notification_list,
                rx.foreach(
                    AppState.notification_list,
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
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
            bg="#2C004BF0", style={"backdrop_filter": "blur(10px)"},
            max_height="300px", overflow_y="auto"
        ),
        on_open_change=lambda open: rx.cond(open, AppState.mark_all_as_read, None)
    )

def public_navbar() -> rx.Component:
    """La barra de navegación pública definitiva, con menú de hamburguesa."""
    icon_color = rx.color_mode_cond("black", "white")
    
    hamburger_menu = rx.menu.root(
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
        rx.box(width="44px", height="44px", padding="0.5em"),
        rx.box(width="38px", height="44px", padding="0.5em"),
        align="center",
        spacing="3",
        justify="end",
    )

    return rx.box(
        rx.grid(
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
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", 
        style={"backdrop_filter": "blur(10px)"},
        on_mount=[AppState.load_notifications],
    )