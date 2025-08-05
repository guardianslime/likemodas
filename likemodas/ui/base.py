# likemodas/ui/base.py (CORREGIDO)

import reflex as rx
from ..state import AppState
from .nav import public_navbar
from .sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

def fixed_color_mode_button() -> rx.Component:
    return rx.box(
        rx.color_mode.button(),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    return rx.cond(
        ~AppState.is_hydrated,
        rx.center(rx.spinner(size="3"), height="100vh"),
        rx.cond(
            AppState.is_admin,
            # --- LAYOUT DE ADMIN RESPONSIVO ---
            rx.box(
                rx.vstack(
                    rx.hstack(
                        mobile_admin_menu(), rx.spacer(),
                        rx.image(src="/logo.png", width="6em", height="auto"),
                        rx.spacer(), sidebar_dark_mode_toggle_item(),
                        width="100%", padding="0.5em 1em", bg="#2C004B", align="center",
                    ),
                    rx.box(child, padding="1em", width="100%"),
                    display=["flex", "flex", "none", "none", "none"], spacing="0",
                ),
                rx.hstack(
                    sidebar(),
                    rx.box(child, padding="1em", width="100%"),
                    display=["none", "none", "flex", "flex", "flex"],
                    align="start", spacing="0", width="100%", min_height="100vh",
                ),
            ),
            # --- LAYOUT PÚBLICO ---
            rx.box(
                public_navbar(),
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )