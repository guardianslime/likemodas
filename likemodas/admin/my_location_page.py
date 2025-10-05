# likemodas/admin/my_location_page.py

import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_admin
from ..ui.components import searchable_select
from ..ui.base import base_page

@require_admin
def my_location_page_content() -> rx.Component:
    """Página para que el vendedor (admin) configure su ubicación de origen."""
    
    # --- INICIO DE LA CORRECCIÓN DEFINITIVA ---
    # Se replica la estructura de la página de referencia "Información para Envíos"
    page_content = rx.vstack(
        # 1. Títulos principales, igual que en la página de referencia
        rx.heading("Mi Ubicación de Origen", size="8"),
        rx.text(
            "Establece la ciudad, barrio y dirección desde donde envías tus productos. El costo de envío se calculará a partir de esta ubicación.",
            color_scheme="gray", 
            size="4",
        ),
        rx.divider(margin_y="1.5em"),

        # 2. Se envuelve el formulario en un rx.card para darle cuerpo y un fondo distinto
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading("Ubicación de Envío", size="6", width="100%"),
                    rx.grid(
                        # Columna 1: Ciudad
                        rx.vstack(
                            rx.text("Mi Ciudad*"),
                            searchable_select(
                                placeholder="Selecciona tu ciudad...",
                                options=AppState.filtered_seller_cities,
                                on_change_select=AppState.set_seller_profile_city,
                                value_select=AppState.seller_profile_city,
                                search_value=AppState.search_seller_city,
                                on_change_search=AppState.set_search_seller_city,
                                filter_name="seller_city_filter",
                            ),
                            align_items="stretch",
                            spacing="1",
                        ),
                        # Columna 2: Barrio
                        rx.vstack(
                            rx.text("Mi Barrio*"),
                            searchable_select(
                                placeholder="Selecciona tu barrio...",
                                options=AppState.filtered_seller_barrios,
                                on_change_select=AppState.set_seller_profile_barrio,
                                value_select=AppState.seller_profile_barrio,
                                search_value=AppState.search_seller_barrio,
                                on_change_search=AppState.set_search_seller_barrio,
                                filter_name="seller_barrio_filter",
                                is_disabled=~AppState.seller_profile_city,
                            ),
                            align_items="stretch",
                            spacing="1",
                        ),
                        # Fila 2: Dirección
                        rx.vstack(
                            rx.text("Mi Dirección* (Calle, Carrera, Apto, etc.)"),
                            rx.input(
                                name="seller_address",
                                placeholder="Ej: Calle 5 # 10-20",
                                value=AppState.seller_profile_address,
                                on_change=AppState.set_seller_profile_address,
                                required=True
                            ),
                            align_items="stretch",
                            spacing="1",
                            grid_column={"initial": "1", "md": "span 2"},
                        ),
                        columns={"initial": "1", "md": "2"},
                        spacing="4",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.spacer(),
                        rx.button("Guardar Mi Ubicación", type="submit", color_scheme="violet"),
                        width="100%", 
                        margin_top="1.5em"
                    ),
                    spacing="5",
                    width="100%",
                ),
                on_submit=AppState.save_seller_profile,
            ),
            width="100%" # La tarjeta ocupa todo el ancho del contenedor
        ),
        
        # 3. Contenedor principal que centra todo y define el ancho máximo
        align="center",
        spacing="5",
        width="100%",
        max_width="1200px",
    )
    # --- FIN DE LA CORRECCIÓN DEFINITIVA ---
    
    return base_page(page_content)