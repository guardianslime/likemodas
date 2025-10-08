# likemodas/ui/admin_nav.py (NUEVO ARCHIVO)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState

def admin_notification_icon() -> rx.Component:
    """Componente para el icono y menú de notificaciones del VENDEDOR/ADMIN."""
    icon_color = rx.color_mode_cond("black", "white")
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("bell", size=24, color=icon_color),
                rx.cond(
                    AppState.admin_unread_count > 0,
                    rx.box(
                        rx.text(AppState.admin_unread_count, size="1", weight="bold"),
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
                AppState.admin_notifications,
                rx.foreach(
                    AppState.admin_notifications,
                    lambda n: rx.menu.item(
                        rx.vstack(
                            rx.text(
                                n.message,
                                weight=rx.cond(n.is_read, "regular", "bold"),
                                white_space="normal", width="100%", size="2"
                            ),
                            rx.hstack(
                                rx.spacer(),
                                rx.text(n.created_at_formatted, size="1", color_scheme="gray"),
                                width="100%", margin_top="0.25em",
                            ),
                            align_items="start", spacing="1", width="100%",
                        ),
                        on_click=rx.cond(n.url, rx.redirect(n.url), AppState.do_nothing),
                        bg=rx.cond(n.is_read, "transparent", rx.color("violet", 3)),
                        height="auto",
                    )
                ),
                rx.menu.item("No tienes notificaciones.")
            ),
            max_height="400px", overflow_y="auto", min_width="350px",
        ),
        on_open_change=lambda open: rx.cond(open, None, AppState.mark_all_admin_as_read)
    )

def admin_top_bar() -> rx.Component:
    """La barra superior para el panel de admin/vendedor."""
    return rx.hstack(
        rx.spacer(),
        admin_notification_icon(),
        rx.button(
            rx.color_mode_cond(light=rx.icon(tag="sun"), dark=rx.icon(tag="moon")),
            on_click=toggle_color_mode,
            variant="ghost", radius="full",
        ),
        spacing="4",
        align="center",
        width="100%",
        padding_right="1em",
    )