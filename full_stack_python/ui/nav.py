import reflex as rx
import reflex_local_auth
from .. import navigation
from ..navigation.device import DeviceState


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(rx.text(text, size="4", weight="medium"), href=url)


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(navbar_desktop()),
        rx.mobile_and_tablet(navbar_mobile()),
        bg=rx.color("accent", 3),
        padding="1em",
        width="100%",
        on_mount=DeviceState.on_mount,
    )



def navbar_desktop() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.link(
                rx.image(
                    src="/logo.jpg",
                    width="2.25em",
                    height="auto",
                    border_radius="25%",
                ),
                href="/",
            ),
            rx.link(
                rx.heading("Likemodas", size="7", weight="bold"),
                href="/",
            ),
            align_items="center",
        ),
        rx.hstack(
            navbar_link("Home", "/"),
            navbar_link("About", "/about"),
            navbar_link("Articulos", "/articles"),
            navbar_link("Galería", "/blog/page"),
            navbar_link("Promociones", "/pricing"),
            navbar_link("Contacto", "/contact"),
            spacing="5",
        ),
        rx.hstack(
            rx.link(
                rx.button("Register", size="3", variant="outline"),
                href="/register",
            ),
            rx.link(
                rx.button("Login", size="3", variant="outline"),
                href="/login",
            ),
            spacing="4",
            justify="end",
        ),
        justify="between",
        align_items="center",
        width="100%",
    )


def navbar_mobile() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.image(
                src="/logo.jpg",
                width="2em",
                height="auto",
                border_radius="25%",
            ),
            rx.heading("Likemodas", size="6", weight="bold"),
            align_items="center",
        ),
        rx.menu.root(
            rx.menu.trigger(rx.icon("menu", size=30)),
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
            justify="end",
        ),
        justify="between",
        align_items="center",
        width="100%",
    )
