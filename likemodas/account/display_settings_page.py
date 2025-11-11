import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout

def display_settings_card() -> rx.Component:
    """Tarjeta con las opciones de visualización."""
    return rx.card(
        rx.vstack(
            rx.heading("Configuración de Visualización", size="6"),
            rx.text(
                "Elige cómo prefieres ver las tarjetas de productos en la tienda.",
                size="3",
                color_scheme="gray"
            ),
            rx.divider(margin_y="1em"),
            
            rx.hstack(
                rx.vstack(
                    rx.text("Forzar Tema del Sitio", weight="bold", size="4"),
                    rx.text(
                        "Ignora el 'Modo Artista' del vendedor y muestra todas las tarjetas "
                        "según el tema claro/oscuro de tu navegador.",
                        size="2",
                        color_scheme="gray",
                        max_width="450px",
                    ),
                    align_items="start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.switch(
                    is_checked=AppState.force_site_theme,
                    on_change=AppState.set_force_site_theme,
                    size="3",
                    color_scheme="violet"
                ),
                align_items="center",
                width="100%",
            ),
            
            rx.callout(
                rx.text(
                    rx.cond(
                        AppState.force_site_theme,
                        "Modo Forzado: Las tarjetas de producto ahora coincidirán con el tema de tu navegador (claro u oscuro).",
                        "Modo Adaptativo: Estás viendo los estilos personalizados (Modo Artista) creados por cada vendedor."
                    )
                ),
                icon="info", # <-- Se pasa el nombre del icono como un string
                color_scheme=rx.cond(AppState.force_site_theme, "blue", "gray"),
                variant="soft",
                margin_top="1.5em",
            ),
            
            spacing="5",
            width="100%",
        ),
        width="100%",
        max_width="700px",
    )

@reflex_local_auth.require_login
def display_settings_page() -> rx.Component:
    """Página de configuración de visualización."""
    
    page_content = rx.vstack(
        rx.heading("Visualización", size="8", text_align="center"),
        rx.text(
            "Personaliza tu experiencia de navegación en la tienda.",
            size="4",
            color_scheme="gray",
            text_align="center",
        ),
        rx.divider(margin_y="1.5em"),
        
        display_settings_card(),
        
        align="center",
        width="100%",
        max_width="1200px",
        spacing="5",
    )
    
    return account_layout(page_content)