import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_admin
from ..ui.components import searchable_select

@require_admin
def seller_profile_page() -> rx.Component:
    """Página para que el vendedor (admin) configure su ubicación de origen."""
    return rx.container(
        rx.vstack(
            rx.heading("Mi Ubicación de Origen", size="7"),
            rx.text(
                "Establece la ciudad, barrio y dirección desde donde envías tus productos.",
                "El costo de envío se calculará a partir de esta ubicación.",
                margin_bottom="1.5em"
            ),
            rx.form(
                rx.vstack(
                    # --- INICIO DE LA MODIFICACIÓN ---
                    
                    # 1. Nuevo selector de búsqueda para la CIUDAD
                    rx.text("Mi Ciudad*", weight="bold"),
                    searchable_select(
                        placeholder="Selecciona tu ciudad...",
                        options=AppState.filtered_seller_cities, # Usa la nueva propiedad
                        on_change_select=AppState.set_seller_profile_city, # Nuevo setter
                        value_select=AppState.seller_profile_city,
                        search_value=AppState.search_seller_city, # Nuevo estado de búsqueda
                        on_change_search=AppState.set_search_seller_city, # Nuevo setter de búsqueda
                        filter_name="seller_city_filter",
                    ),

                    # 2. El selector de BARRIO ahora es dinámico
                    rx.text("Mi Barrio*", weight="bold", margin_top="1em"),
                    searchable_select(
                        placeholder="Selecciona tu barrio...",
                        options=AppState.filtered_seller_barrios, # Usa la propiedad dinámica
                        on_change_select=AppState.set_seller_profile_barrio,
                        value_select=AppState.seller_profile_barrio,
                        search_value=AppState.search_seller_barrio,
                        on_change_search=AppState.set_search_seller_barrio,
                        filter_name="seller_barrio_filter",
                        # Se deshabilita hasta que se elija una ciudad
                        is_disabled=~AppState.seller_profile_city, 
                    ),

                    # --- FIN DE LA MODIFICACIÓN ---
                    
                    rx.text("Mi Dirección*", weight="bold", margin_top="1em"),
                    rx.input(
                        name="seller_address",
                        placeholder="Ej: Calle 5 # 10-20",
                        value=AppState.seller_profile_address,
                        on_change=AppState.set_seller_profile_address,
                        required=True
                    ),
                    rx.button("Guardar Mi Ubicación", type="submit", margin_top="2em", color_scheme="violet"),
                    spacing="3",
                    align_items="stretch"
                ),
                on_submit=AppState.save_seller_profile,
            ),
            align="stretch",
            width="100%",
            max_width="600px",
        ),
        padding_top="2em",
        min_height="85vh",
    )