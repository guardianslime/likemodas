import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # 📱 Menú hamburguesa a la izquierda
            rx.menu.root(
                rx.menu.trigger(
                    rx.icon("menu", box_size=rx.breakpoints(sm="1.8em", md="2em", lg="2.3em"))
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

            # 🧢 Logo + título al centro
            rx.hstack(
                rx.image(
                    src="/logo.jpg",
                    width=rx.breakpoints(sm="2em", md="2.5em", lg="3em"),
                    height="auto",
                    border_radius="25%",
                ),
                rx.heading("Likemodas", size=rx.breakpoints(sm="6", md="7", lg="8"), weight="bold"),
                align_items="center",
            ),

            rx.spacer(),

            # 🔍 Barra de búsqueda al final (derecha o centrada si hay espacio)
            rx.input(
                placeholder="Buscar productos...",
                width=rx.breakpoints(sm="40%", md="40%", lg="30%"),
                height="2.5em",
                padding_x="1em",
                border_radius="md",
                border_width="1px",
                border_color="gray",
                background_color="white",
                color="black",
                font_size=rx.breakpoints(sm="1", md="2", lg="3"),
            ),

            width="100%",
            align_items="center",
            spacing="4",
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        width="100%",
        on_mount=DeviceState.on_mount,
    )
