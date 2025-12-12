# likemodas/admin/my_location_page.py

import reflex as rx
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from ..ui.components import searchable_select, multi_select_component
from ..ui.base import base_page

@require_panel_access
def my_location_page_content() -> rx.Component:
    
    page_content = rx.vstack(
        rx.heading("Configuración de Envíos", size="8"),
        rx.text(
            "Gestiona tu origen de envío y las zonas donde ofreces beneficios especiales.",
            color_scheme="gray", size="4", text_align="center"
        ),
        
        # 1. ORIGEN (2 COLUMNAS para Ciudad y Barrio)
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading("1. Mi Ubicación de Origen", size="6"),
                    rx.grid(
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
                                columns="2" # ✨ 2 COLUMNAS PARA CIUDADES
                            ),
                            width="100%"
                        ),
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
                                columns="2" # ✨ 2 COLUMNAS PARA BARRIOS
                            ),
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Dirección Exacta*"),
                            rx.input(
                                name="seller_address",
                                placeholder="Ej: Calle 5 # 10-20",
                                value=AppState.seller_profile_address,
                                on_change=AppState.set_seller_profile_address,
                                required=True
                            ),
                            width="100%",
                            grid_column="span 2"
                        ),
                        columns="2", 
                        spacing="4", 
                        width="100%"
                    ),
                    rx.button("Guardar Origen", type="submit", color_scheme="violet", width="100%", margin_top="1em"),
                ),
                on_submit=AppState.save_seller_profile,
            ),
            width="100%"
        ),

        # 2. DESTINO MODA COMPLETA (4 COLUMNAS)
        rx.card(
            rx.vstack(
                rx.heading("2. Destinos: Moda Completa", size="6"),
                rx.text(
                    "Ciudades con envío gratis por monto mínimo. Vacío = Todo el país.",
                    color_scheme="gray", size="2"
                ),
                rx.divider(),
                
                multi_select_component(
                    placeholder="Buscar ciudades...",
                    options=AppState.all_cities_list,
                    selected_items=AppState.seller_moda_completa_cities,
                    add_handler=AppState.add_moda_city,
                    remove_handler=AppState.remove_moda_city,
                    prop_name="seller_moda_completa_cities",
                    search_value=AppState.search_moda_city,
                    on_change_search=AppState.set_search_moda_city,
                    filter_name="moda_city_filter",
                    columns="4" # ✨ 4 COLUMNAS (MÁS AMPLIO)
                ),
                rx.button("Guardar Moda Completa", on_click=AppState.save_seller_destinations, color_scheme="violet", width="100%")
            ),
            width="100%"
        ),

        # 3. DESTINO ENVÍO COMBINADO (4 COLUMNAS) - NUEVO
        rx.card(
            rx.vstack(
                rx.heading("3. Destinos: Envío Combinado", size="6"),
                rx.text(
                    "Ciudades donde permites combinar productos. Vacío = Todo el país.",
                    color_scheme="gray", size="2"
                ),
                rx.divider(),
                
                multi_select_component(
                    placeholder="Buscar ciudades...",
                    options=AppState.all_cities_list_combined, # Usamos la nueva variable filtrada
                    selected_items=AppState.seller_combined_shipping_cities,
                    add_handler=AppState.add_combined_city,
                    remove_handler=AppState.remove_combined_city,
                    prop_name="seller_combined_shipping_cities",
                    search_value=AppState.search_combined_city,
                    on_change_search=AppState.set_search_combined_city,
                    filter_name="combined_city_filter",
                    columns="4" # ✨ 4 COLUMNAS (MÁS AMPLIO)
                ),
                rx.button("Guardar Envío Combinado", on_click=AppState.save_seller_destinations, color_scheme="violet", width="100%")
            ),
            width="100%"
        ),

        align="center",
        spacing="5",
        width="100%",
        max_width="1000px", # Un poco más ancho para las 4 columnas
        padding_bottom="3em"
    )
    
    return base_page(rx.center(page_content))