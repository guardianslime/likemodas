import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # LOGO
            rx.image(
                src="/logo.jpg",
                width=rx.breakpoints(sm="2em", md="2.5em", lg="3em"),
                height="auto",
                border_radius="25%",
            ),

            # Menú hamburguesa
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

            # Barra de búsqueda — crece proporcionalmente con espacio disponible
            rx.spacer(),

            rx.input(
                placeholder="Buscar productos...",
                width=rx.breakpoints(sm="55%", md="60%", lg="65%"),
                height="2.5em",
                padding_x="1em",
                border_radius="full",  # ✅ Bordes redondeados
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
        padding_y="1em",
        padding_x="1.5em",
        width="100%",
        on_mount=DeviceState.on_mount,
    )
