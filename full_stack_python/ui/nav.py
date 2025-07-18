import reflex as rx
from .. import navigation
from ..navigation.device import NavDeviceState
from .search_state import SearchState
from ..cart.state import CartState
from ..auth.state import SessionState
# Se importa el nuevo estado de notificaciones
from ..notifications.state import NotificationState

def notification_icon() -> rx.Component:
    """Ícono de notificaciones que las marca como leídas al abrir el menú."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("bell", size=28),
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
            bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
            style={"backdrop_filter": "blur(10px)"},
            max_height="300px",
            overflow_y="auto"
        ),
        # --- ✨ CAMBIO CLAVE: Usamos el evento on_open_change ---
        # Esto se dispara cuando el menú se abre, que es el momento perfecto
        # para marcar las notificaciones como leídas.
        on_open_change=lambda open: rx.cond(open, NotificationState.mark_all_as_read, None)
    )

def public_navbar() -> rx.Component:
    """
    Una barra de navegación superior fija para todas las páginas públicas.
    con el menú a la izquierda y estilos de color personalizados.
    """
    return rx.box(
        rx.hstack(
            # --- Lado izquierdo (Menú y Logo) ---
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.icon("menu", size=24, color=rx.color_mode_cond("black", "white")),
                            variant="ghost"
                        )
                    ),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=navigation.NavState.to_home),
                        rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                        rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                        rx.menu.separator(),
                        rx.cond(
                            SessionState.is_authenticated,
                            rx.fragment(
                                rx.menu.item("Mis Compras", on_click=navigation.NavState.to_my_purchases),
                                rx.menu.item("Logout", on_click=navigation.NavState.to_logout),
                            ),
                            rx.fragment(
                                rx.menu.item("Login", on_click=navigation.NavState.to_login),
                                rx.menu.item("Register", on_click=navigation.NavState.to_register),
                            )
                        ),
                        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
                        style={"backdrop_filter": "blur(10px)"},
                    ),
                ),
                rx.image(
                    src="/logo.jpg",
                    width="8em",
                    height="auto",
                    border_radius="md",
                ),
                align="center",
                spacing="4"
            ),
            
            # --- Centro (Barra de Búsqueda) ---
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["40%", "50%", "60%", "65%"],
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
                border_width="1px",
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            
            # --- Lado Derecho (Iconos) ---
            rx.hstack(
                rx.cond(
                    SessionState.is_authenticated,
                    # Se envuelve en un fragmento para añadir el nuevo ícono
                    rx.fragment(
                        # ÍCONO DE NOTIFICACIONES AÑADIDO
                        notification_icon(),
                        
                        # Ícono del carrito (existente)
                        rx.link(
                            rx.box(
                                rx.icon("shopping-cart", size=28),
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
                align="center",
                spacing="4",
            ),
            
            justify="between",
            align="center",
            width="100%",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
        style={"backdrop_filter": "blur(10px)"},
        # CAMBIO: Se carga el estado de las notificaciones al montar la barra
        on_mount=[NavDeviceState.on_mount, NotificationState.load_notifications],
    )


def navbar() -> rx.Component:
    """
    Navbar original y completo. Se mantiene aquí por si se necesita en otras partes.
    """
    return rx.box(
        # Grupo Izquierdo: Logo y Menú
        rx.box(
            rx.image(
                src="/logo.jpg",
                width=rx.breakpoints(sm="6em", md="8em", lg="10em"),
                height="auto",
                border_radius="md",
            ),
            rx.menu.root(
                rx.menu.trigger(
                    rx.icon("menu", box_size=rx.breakpoints(sm="2em", md="2.3em", lg="2.5em"))
                ),
                rx.menu.content(
                    rx.menu.item("Home", on_click=navigation.NavState.to_home),
                    rx.menu.item("Articles", on_click=navigation.NavState.to_articles),
                    rx.menu.item("Blog", on_click=navigation.NavState.to_blog),
                    rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                    rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                    rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                    rx.menu.separator(),
                    rx.menu.item("Login", on_click=navigation.NavState.to_login),
                    rx.menu.item("Register", on_click=navigation.NavState.to_register),
                ),
            ),
            style={
                "display": "flex",
                "align_items": "center",
                "gap": "1rem",
            }
        ),
        # Barra de Búsqueda
        rx.input(
            placeholder="Buscar productos...",
            value=SearchState.search_term,
            on_change=SearchState.update_search,
            on_blur=SearchState.search_action,
            width=rx.breakpoints(sm="55%", md="65%", lg="72%"),
            height=rx.breakpoints(sm="2.8em", md="3em", lg="3.3em"),
            padding_x="4",
            border_radius="full",
            border_width="1px",
            border_color="#ccc",
            background_color="white",
            color="black",
            font_size=rx.breakpoints(sm="1", md="2", lg="3"),
        ),
        # Estilos del contenedor principal
        style={
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "width": "100%",
            "padding_y": "0.75rem",
            "padding_x": "1rem",
        },
        on_mount=NavDeviceState.on_mount,
    )


class SearchState(rx.State):
    search_term: str = ""

    def update_search(self, value: str):
        self.search_term = value
        print(f"🔍 Buscando: {self.search_term}")

    def search_action(self):
        # Aquí puedes navegar a otra página o hacer un filtro
        print(f"🔎 Acción de búsqueda: {self.search_term}")