import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState  # ✅ conecta con el estado


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # 🔷 Logo + texto con más espacio
            rx.hstack(
                rx.image(
                    src="/logo.jpg",
                    width=rx.breakpoints(sm="2.2em", md="2.5em", lg="3em"),
                    height="auto",
                    border_radius="25%",
                ),
                rx.heading(
                    "Likemodas",
                    size=rx.breakpoints(sm="6", md="7", lg="8"),
                    weight="bold",
                    color="white"
                ),
                spacing="1.5em",
                width=rx.breakpoints(sm="auto", md="auto", lg="20%"),
                align_items="center",
            ),

            # 🔍 Barra de búsqueda estirada
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=rx.breakpoints(sm="60%", md="70%", lg="75%"),
                height=rx.breakpoints(sm="2.5em", md="3em", lg="3.5em"),  # ✅ Más gruesa
                padding_x="1.2em",
                border_radius="full",
                border_width="1px",
                border_color="#ccc",
                background_color="white",
                color="black",
                font_size=rx.breakpoints(sm="1", md="2", lg="3"),
            ),

            # ☰ Menú hamburguesa a la derecha
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

            width="100%",
            align_items="center",
            spacing="1.5em",
            wrap="wrap",
        ),
        bg=rx.color("accent", 3),
        padding_y="1em",
        padding_x="1.5em",
        width="100%",
        on_mount=DeviceState.on_mount,
    )
