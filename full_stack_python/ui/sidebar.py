import reflex as rx
from reflex.style import toggle_color_mode

from ..auth.state import SessionState
from .. import navigation
from ..navigation import routes

def sidebar_user_item() -> rx.Component:
    user_info_obj = SessionState.authenticated_user_info
    username_via_user_abj = rx.cond(SessionState.authenticated_username, SessionState.authenticated_username, "Account")
    return rx.cond(
        user_info_obj,
        rx.hstack(
            rx.icon_button(
                rx.icon("user"),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.box(
                    rx.text(
                        username_via_user_abj,
                        size="3",
                        weight="bold",
                    ),
                    rx.text(
                        f"{user_info_obj.email}",
                        size="2",
                        weight="medium",
                    ),
                    width="100%",
                ),
                spacing="0",
                align="start",
                justify="start",
                width="100%",
            ),
            padding_x="0.5rem",
            align="center",
            justify="start",
            width="100%",
        ),
        rx.fragment("")
    )

def sidebar_logout_item() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("log-out"),
            rx.text("Logout", size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.7rem",
            border_radius="0.375rem",
            _hover={
                "background_color": rx.color("accent", 4)
            }
        ),
        cursor="pointer",
        # --- ARREGLO DEFINITIVO ---
        # En lugar de llamar a una función, redirigimos a la ruta de logout.
        on_click=rx.redirect(navigation.routes.LOGOUT_ROUTE)
    )

def sidebar_dark_mode_toggle_item() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("sun-moon"),
            rx.text("Toggle Theme", size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.7rem",
            border_radius="0.375rem",
            _hover={
                "background_color": rx.color("accent", 4)
            }
        ),
        cursor="pointer",
        on_click=toggle_color_mode
    )

def sidebar_item(name: str, url: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(name, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.7rem",
            border_radius="0.375rem",
            _hover={
                "background_color": rx.color("accent", 4)
            }
        ),
        href=url,
        width="100%",
    )

def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Home", routes.HOME_ROUTE),
        sidebar_item("About", routes.ABOUT_US_ROUTE),
        sidebar_item("Pricing", routes.PRICING_ROUTE),
        sidebar_item("Articles", routes.ARTICLE_LIST_ROUTE),
        sidebar_item("Blog Posts", routes.BLOG_POSTS_ROUTE),
        sidebar_item("Nuevo Contacto", routes.CONTACT_V2_ADD_ROUTE),
        width="100%",
        align_items="start",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.vstack(
                sidebar_items(),
                rx.spacer(),
                rx.vstack(
                    rx.vstack(
                        sidebar_dark_mode_toggle_item(),
                        sidebar_logout_item(),
                        width="100%",
                        spacing="1",
                    ),
                    rx.divider(margin="0"),
                    sidebar_user_item(),
                    width="100%",
                    spacing="5",
                ),
                height="94vh",
                padding_y="2em",
                border_right=f"1px solid {rx.color('accent', 6)}",
            ),
            padding_x="1em",
        ),
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(
                    rx.icon("menu", size=30),
                ),
                rx.drawer.portal(
                     rx.drawer.overlay(
                        z_index="19",
                        bg="rgba(0,0,0,0.2)"
                     ),
                     rx.drawer.content(
                        rx.vstack(
                            rx.box(
                                rx.drawer.close(
                                    rx.icon("x", size=30)
                                ),
                                width="100%",
                            ),
                            sidebar_items(),
                            rx.spacer(),
                            rx.vstack(
                                rx.vstack(
                                    sidebar_dark_mode_toggle_item(),
                                    sidebar_logout_item(),
                                    width="100%",
                                    spacing="1",
                                ),
                                rx.divider(margin="0"),
                                sidebar_user_item(),
                                width="100%",
                                spacing="5",
                            ),
                            spacing="5",
                            width="100%",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="20em",
                        padding="1.5em",
                        bg=rx.color("accent", 2),
                    ),
                    width="100%",
                ),
                direction="left",
            ),
            padding="1em",
        ),
    )