import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component

def floating_filter_panel() -> rx.Component:
    """
    Panel de filtros con selección múltiple, lógica condicional por categoría
    y un layout robusto con barra de desplazamiento funcional.
    """
    
    # --- Bloques de UI para cada grupo de filtros ---
    
    filtros_ropa = rx.vstack(
        rx.divider(), 
        rx.text("Filtros de Ropa", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", 
            options=AppState.filtered_tipos_ropa,
            selected_items=AppState.filter_tipos_general, 
            add_handler=lambda val: AppState.add_filter_value("filter_tipos_general", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tipos_general", item),
            prop_name="filter_tipos_general",
            search_value=AppState.search_tipo_prenda, 
            on_change_search=AppState.set_search_tipo_prenda,
            filter_name="ropa_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir talla...", 
            options=AppState.filtered_tallas_ropa,
            selected_items=AppState.filter_tallas, 
            add_handler=lambda val: AppState.add_filter_value("filter_tallas", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tallas", item),
            prop_name="filter_tallas",
            search_value=AppState.search_talla, 
            on_change_search=AppState.set_search_talla,
            filter_name="ropa_talla_filter",
        ),
        multi_select_component(
            placeholder="Añadir tela...", 
            options=AppState.filtered_materiales,
            selected_items=AppState.filter_materiales_tela, 
            add_handler=lambda val: AppState.add_filter_value("filter_materiales_tela", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_materiales_tela", item),
            prop_name="filter_materiales_tela",
            search_value=AppState.search_material_tela, 
            on_change_search=AppState.set_search_material_tela,
            filter_name="ropa_material_filter",
        ),
        spacing="2", 
        align_items="start", 
        width="100%"
    )

    filtros_calzado = rx.vstack(
        rx.divider(), 
        rx.text("Filtros de Calzado", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", 
            options=AppState.filtered_tipos_zapatos,
            selected_items=AppState.filter_tipos_general, 
            add_handler=lambda val: AppState.add_filter_value("filter_tipos_general", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tipos_general", item),
            prop_name="filter_tipos_general",
            search_value=AppState.search_tipo_zapato, 
            on_change_search=AppState.set_search_tipo_zapato,
            filter_name="calzado_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir número...", 
            options=AppState.filtered_numeros_calzado,
            selected_items=AppState.filter_numeros_calzado, 
            add_handler=lambda val: AppState.add_filter_value("filter_numeros_calzado", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_numeros_calzado", item),
            prop_name="filter_numeros_calzado",
            search_value=AppState.search_numero_calzado, 
            on_change_search=AppState.set_search_numero_calzado,
            filter_name="calzado_numero_filter",
        ),
        multi_select_component(
            placeholder="Añadir material...", 
            options=AppState.filtered_materiales,
            selected_items=AppState.filter_materiales_tela, 
            add_handler=lambda val: AppState.add_filter_value("filter_materiales_tela", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_materiales_tela", item),
            prop_name="filter_materiales_tela",
            search_value=AppState.search_material_tela, 
            on_change_search=AppState.set_search_material_tela,
            filter_name="calzado_material_filter",
        ),
        spacing="2", 
        align_items="start", 
        width="100%"
    )
    
    filtros_mochilas = rx.vstack(
        rx.divider(), 
        rx.text("Filtros de Mochilas", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...", 
            options=AppState.filtered_tipos_mochilas,
            selected_items=AppState.filter_tipos_general, 
            add_handler=lambda val: AppState.add_filter_value("filter_tipos_general", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tipos_general", item),
            prop_name="filter_tipos_general",
            search_value=AppState.search_tipo_mochila, 
            on_change_search=AppState.set_search_tipo_mochila,
            filter_name="mochila_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir material...", 
            options=AppState.filtered_materiales,
            selected_items=AppState.filter_materiales_tela, 
            add_handler=lambda val: AppState.add_filter_value("filter_materiales_tela", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_materiales_tela", item),
            prop_name="filter_materiales_tela",
            search_value=AppState.search_material_tela, 
            on_change_search=AppState.set_search_material_tela,
            filter_name="mochila_material_filter",
        ),
        spacing="2", 
        align_items="start", 
        width="100%"
    )
    
    filtros_generales = rx.vstack(
        rx.divider(), 
        rx.text("Filtros Generales", weight="bold"),
        multi_select_component(
            placeholder="Añadir tipo...",
            options=AppState.filtered_tipos_general,
            selected_items=AppState.filter_tipos_general,
            add_handler=lambda val: AppState.add_filter_value("filter_tipos_general", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tipos_general", item),
            prop_name="filter_tipos_general",
            search_value=AppState.search_tipo_general,
            on_change_search=AppState.set_search_tipo_general,
            filter_name="general_tipo_filter",
        ),
        multi_select_component(
            placeholder="Añadir material...", 
            options=AppState.filtered_materiales,
            selected_items=AppState.filter_materiales_tela, 
            add_handler=lambda val: AppState.add_filter_value("filter_materiales_tela", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_materiales_tela", item),
            prop_name="filter_materiales_tela",
            search_value=AppState.search_material_tela, 
            on_change_search=AppState.set_search_material_tela,
            filter_name="general_material_filter",
        ),
        multi_select_component(
            placeholder="Añadir talla/medida...",
            options=AppState.filtered_medidas_general,
            selected_items=AppState.filter_tallas,
            add_handler=lambda val: AppState.add_filter_value("filter_tallas", val),
            remove_handler=lambda item: AppState.remove_filter_value("filter_tallas", item),
            prop_name="filter_tallas",
            search_value=AppState.search_talla,
            on_change_search=AppState.set_search_talla,
            filter_name="general_talla_filter",
        ),
        spacing="2", 
        align_items="stretch", 
        width="100%"
    )

    # El resto del componente permanece igual
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.heading("Filtros", size="6"),
                    rx.spacer(),
                    rx.button("Limpiar", on_click=AppState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                    justify="between", 
                    align_items="center", 
                    width="100%",
                    flex_shrink=0,
                ),
                rx.divider(),
                rx.scroll_area(
                    rx.vstack(
                        rx.vstack(
                            rx.text("Precio", weight="bold"),
                            rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                            rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                            spacing="2", 
                            align_items="start", 
                            width="100%"
                        ),
                        rx.vstack(
                            rx.divider(),
                            rx.hstack(
                                rx.text("Envío Gratis", size="3"),
                                rx.spacer(),
                                rx.switch(
                                    is_checked=AppState.filter_free_shipping,
                                    on_change=AppState.set_filter_free_shipping,
                                ),
                                width="100%",
                                justify="between",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Moda Completa", size="3"),
                                rx.spacer(),
                                rx.switch(
                                    is_checked=AppState.filter_complete_fashion,
                                    on_change=AppState.set_filter_complete_fashion,
                                ),
                                width="100%",
                                justify="between",
                                align="center",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.cond(
                            (AppState.current_category != "") & (AppState.current_category != "todos"),
                            rx.cond(
                                AppState.current_category == Category.ROPA.value,
                                filtros_ropa,
                                rx.cond(
                                    AppState.current_category == Category.CALZADO.value,
                                    filtros_calzado,
                                    rx.cond(
                                        AppState.current_category == Category.MOCHILAS.value,
                                        filtros_mochilas,
                                        rx.fragment()
                                    )
                                )
                            ),
                            filtros_generales
                        ),
                        spacing="4",
                        padding_right="1.5em",
                        width="100%",
                    ),
                    type="auto", 
                    scrollbars="vertical",
                ),
                spacing="4",
                padding="1em",
                height="100%",
                width="280px",
                bg=rx.color("gray", 2),
            ),
            rx.box(
                rx.text("Filtros", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)", "padding": "0.5em 0.09em", "font_weight": "bold", "letter_spacing": "2px", "color": "white"}),
                on_click=AppState.toggle_filters, 
                cursor="pointer", 
                bg=rx.color("violet", 9),
                border_radius="0 8px 8px 0", 
                height="120px", 
                display="flex", 
                align_items="center"
            ),
            align_items="start", 
            spacing="0",
            height="100%",
        ),
        height="95vh",
        max_height="800px",
        position="fixed",
        top="50%",
        left="0",
        transform=rx.cond(AppState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out",
        z_index=1000,
    )

