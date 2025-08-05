# likemodas/ui/base.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
from ..state import AppState
from .nav import public_navbar
# ✅ ¡Importante! Importa el nuevo esqueleto y los componentes de la barra lateral.
from .skeletons import skeleton_navbar 
from .sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

def fixed_color_mode_button() -> rx.Component:
    return rx.box(
        rx.color_mode.button(),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    # La guarda de hidratación ahora envuelve TODA la lógica de renderizado.
    return rx.cond(
        ~AppState.is_hydrated,
        # --- LAYOUT ESQUELETO (Para SSR y renderizado inicial del cliente) ---
        # Muestra una versión estática y sin estado del layout. Esto es clave.
        rx.box(
            skeleton_navbar(),  # Usa el nuevo navbar esqueleto.
            rx.box(
                # El 'child' se pasa aquí también, permitiendo que muestre su PROPIO esqueleto.
                child,
                padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"
            ),
            width="100%",
        ),
        # --- LAYOUT COMPLETAMENTE HIDRATADO (Seguro para renderizar) ---
        # Una vez que el cliente está listo, se renderiza el layout real con estado.
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
            # --- LAYOUT PÚBLICO (Ahora seguro y sin glitches) ---
            rx.box(
                public_navbar(),  # El navbar real y con estado.
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),  # El botón de modo de color real.
                width="100%",
            )
        )
    )