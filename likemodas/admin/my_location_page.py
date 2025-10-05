# likemodas/admin/my_location_page.py

import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_admin
from ..ui.components import searchable_select
from ..ui.base import base_page

@require_admin
def my_location_page_content() -> rx.Component:
    """Página para que el vendedor (admin) configure su ubicación de origen."""
    
    # --- INICIO DE LA REESTRUCTURACIÓN CON RX.GRID ---
    page_content = rx.vstack(
        rx.heading("Mi Ubicación de Origen", size="8"),
        rx.text(
            "Establece la ciudad, barrio y dirección desde donde envías tus productos. El costo de envío se calculará a partir de esta ubicación.",
            color_scheme="gray", 
            size="4",
            text_align="center"
        ),
        rx.card(
            rx.form(
                rx.vstack(
                    # Usamos un grid para distribuir los campos del formulario
                    rx.grid(
                        # Columna 1: Ciudad
                        rx.vstack(
                            rx.text("Mi Ciudad*", weight="bold"),
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
                            spacing="2",
                        ),
                        # Columna 2: Barrio
                        rx.vstack(
                            rx.text("Mi Barrio*", weight="bold"),
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
                            spacing="2",
                        ),
                        # Fila 2: Dirección (ocupa ambas columnas)
                        rx.vstack(
                            rx.text("Mi Dirección*", weight="bold"),
                            rx.input(
                                name="seller_address",
                                placeholder="Ej: Calle 5 # 10-20",
                                value=AppState.seller_profile_address,
                                on_change=AppState.set_seller_profile_address,
                                required=True
                            ),
                            align_items="stretch",
                            spacing="2",
                            # Esta propiedad hace que ocupe todo el ancho del grid
                            grid_column={"initial": "span 1", "md": "span 2"},
                        ),
                        # Configuración del grid: 1 columna en móvil, 2 en pantallas medianas y grandes
                        columns={"initial": "1", "md": "2"},
                        spacing="4",
                        width="100%",
                    ),
                    rx.button("Guardar Mi Ubicación", type="submit", margin_top="2em", color_scheme="violet", width="100%"),
                    spacing="4",
                    align_items="stretch"
                ),
                on_submit=AppState.save_seller_profile,
            ),
        ),
        align="center",
        spacing="5",
        width="100%",
        max_width="960px",
    )
    # --- FIN DE LA REESTRUCTURACIÓN ---
    
    return base_page(
        rx.center(
            page_content,
            min_height="85vh"
        )
    )