# likemodas/admin/my_location_page.py

import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_admin
from ..ui.components import searchable_select
from ..ui.base import base_page

@require_admin
def my_location_page_content() -> rx.Component:
    """Página para que el vendedor (admin) configure su ubicación de origen."""
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
                    rx.text("Mi Barrio*", weight="bold", margin_top="1em"),
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
                    rx.text("Mi Dirección*", weight="bold", margin_top="1em"),
                    rx.input(
                        name="seller_address",
                        placeholder="Ej: Calle 5 # 10-20",
                        value=AppState.seller_profile_address,
                        on_change=AppState.set_seller_profile_address,
                        required=True
                    ),
                    rx.button("Guardar Mi Ubicación", type="submit", margin_top="2em", color_scheme="violet"),
                    spacing="4",
                    align_items="stretch"
                ),
                on_submit=AppState.save_seller_profile,
            ),
        ),
        align="center",
        spacing="5",
        width="100%",
        # --- ✨ CORRECCIÓN CLAVE: Aumentamos el ancho máximo ---
        max_width="960px", 
    )
    
    return base_page(
        rx.center(
            page_content,
            min_height="85vh"
        )
    )