import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # 🖼 LOGO ampliado (para incluir texto en la imagen)
            rx.image(
                src="/logo.jpg",
                width=rx.breakpoints(sm="6em", md="8em", lg="10em"),  # ✅ más ancho para contener texto
                height="auto",
                border_radius="md",
            ),

            # ☰ Menú hamburguesa
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

            # 🔍 Barra de búsqueda estirada
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

            width="100%",
            align_items="center",
            spacing="4",
            wrap="wrap",
        ),
        bg=rx.color("accent", 3),
        padding_y="4",
        padding_x="6",
        width="100%",
        on_mount=DeviceState.on_mount,
    )
