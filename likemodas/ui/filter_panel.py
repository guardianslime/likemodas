# likemodas/ui/filter_panel.py (VERSIÓN CORREGIDA CON FILTROS POR CATEGORÍA)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component

def floating_filter_panel() -> rx.Component:
    """
    Panel de filtros con selección múltiple y lógica condicional
    para mostrar filtros específicos por categoría.
    """
    return rx.box(
        rx.hstack(
            rx.vstack(
                # Encabezado del panel (Limpiar Filtros)
                rx.hstack(
                    rx.heading("Filtros", size="6"),
                    rx.spacer(),
                    rx.button("Limpiar", on_click=AppState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                    justify="between", align_items="center", width="100%"
                ),
                rx.divider(),
                
                # Filtro de Precio (siempre visible)
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                    rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                    spacing="2", align_items="start", width="100%"
                ),

                # --- ✨ LÓGICA CONDICIONAL RESTAURADA ---
                # Muestra filtros específicos solo si se ha seleccionado una categoría.
                rx.cond(
                    (AppState.current_category != "") & (AppState.current_category != "todos"),
                    rx.fragment(
                        # --- FILTROS PARA ROPA ---
                        rx.cond(
                            AppState.current_category == Category.ROPA.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Ropa", weight="bold"),
                                multi_select_component(
                                    placeholder="Añadir tipo...",
                                    options=AppState.filtered_tipos_ropa,
                                    selected_items=AppState.filter_tipos_prenda,
                                    add_handler=AppState.add_filter_value,
                                    remove_handler=AppState.remove_filter_value,
                                    prop_name="filter_tipos_prenda",
                                    search_value=AppState.search_tipo_prenda,
                                    on_change_search=AppState.set_search_tipo_prenda,
                                    filter_name="ropa_tipo_filter",
                                ),
                                multi_select_component(
                                    placeholder="Añadir talla...",
                                    options=AppState.filtered_tallas_ropa,
                                    selected_items=AppState.filter_tallas,
                                    add_handler=AppState.add_filter_value,
                                    remove_handler=AppState.remove_filter_value,
                                    prop_name="filter_tallas",
                                    search_value=AppState.search_talla,
                                    on_change_search=AppState.set_search_talla,
                                    filter_name="ropa_talla_filter",
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        
                        # --- FILTROS PARA CALZADO ---
                        rx.cond(
                            AppState.current_category == Category.CALZADO.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Calzado", weight="bold"),
                                multi_select_component(
                                    placeholder="Añadir tipo...",
                                    options=AppState.filtered_tipos_zapatos,
                                    selected_items=AppState.filter_tipos_zapato,
                                    add_handler=AppState.add_filter_value,
                                    remove_handler=AppState.remove_filter_value,
                                    prop_name="filter_tipos_zapato",
                                    search_value=AppState.search_tipo_zapato,
                                    on_change_search=AppState.set_search_tipo_zapato,
                                    filter_name="calzado_tipo_filter",
                                ),
                                multi_select_component(
                                    placeholder="Añadir número...",
                                    options=AppState.filtered_numeros_calzado,
                                    selected_items=AppState.filter_numeros_calzado,
                                    add_handler=AppState.add_filter_value,
                                    remove_handler=AppState.remove_filter_value,
                                    prop_name="filter_numeros_calzado",
                                    search_value=AppState.search_numero_calzado,
                                    on_change_search=AppState.set_search_numero_calzado,
                                    filter_name="calzado_numero_filter",
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                        
                        # --- FILTROS PARA MOCHILAS ---
                        rx.cond(
                            AppState.current_category == Category.MOCHILAS.value,
                            rx.vstack(
                                rx.divider(), rx.text("Filtros de Mochilas", weight="bold"),
                                multi_select_component(
                                    placeholder="Añadir tipo...",
                                    options=AppState.filtered_tipos_mochilas,
                                    selected_items=AppState.filter_tipos_mochila,
                                    add_handler=AppState.add_filter_value,
                                    remove_handler=AppState.remove_filter_value,
                                    prop_name="filter_tipos_mochila",
                                    search_value=AppState.search_tipo_mochila,
                                    on_change_search=AppState.set_search_tipo_mochila,
                                    filter_name="mochila_tipo_filter",
                                ),
                                spacing="2", align_items="start", width="100%"
                            )
                        ),
                    ),
                    # --- FILTROS GENERALES (CUANDO NO HAY CATEGORÍA SELECCIONADA) ---
                    rx.fragment(
                        rx.divider(),
                        rx.text("Filtros Generales", weight="bold"),
                        multi_select_component(
                            placeholder="Añadir color...",
                            options=AppState.filtered_colores,
                            selected_items=AppState.filter_colors,
                            add_handler=AppState.add_filter_value,
                            remove_handler=AppState.remove_filter_value,
                            prop_name="filter_colors",
                            search_value=AppState.search_color,
                            on_change_search=AppState.set_search_color,
                            filter_name="general_color_filter",
                        ),
                    )
                ),
                spacing="4", padding="1.5em", bg=rx.color("gray", 2),
                height="100%", width="280px",
            ),
            # Botón para mostrar/ocultar
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_filters, cursor="pointer", bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0", height="120px", display="flex", align_items="center"
            ),
            align_items="center", spacing="0"
        ),
        position="fixed", top="50%", left="0",
        transform=rx.cond(AppState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out", z_index=1000, height="auto",
    )