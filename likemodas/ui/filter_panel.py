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
            selected_items=AppState.filter_tipos_mochila, 
            add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, 
            prop_name="filter_tipos_mochila",
            search_value=AppState.search_tipo_mochila, 
            on_change_search=AppState.set_search_tipo_mochila,
            filter_name="mochila_tipo_filter",
        ),
        spacing="2", 
        align_items="start", 
        width="100%"
    )
    
    filtros_generales = rx.vstack(
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
        multi_select_component(
            placeholder="Añadir material...", 
            options=AppState.filtered_materiales,
            selected_items=AppState.filter_materiales_tela, 
            add_handler=AppState.add_filter_value,
            remove_handler=AppState.remove_filter_value, 
            prop_name="filter_materiales_tela",
            search_value=AppState.search_material_tela, 
            on_change_search=AppState.set_search_material_tela,
            filter_name="general_material_filter",
        ),
        spacing="2", 
        align_items="stretch", 
        width="100%"
    )

    # --- Contenedor principal del panel ---
    return rx.box(
        rx.hstack(
            # Columna izquierda: El panel de filtros
            rx.vstack(
                # Encabezado con título y botón de limpiar
                rx.hstack(
                    rx.heading("Filtros", size="6"),
                    rx.spacer(),
                    rx.button("Limpiar", on_click=AppState.clear_all_filters, size="1", variant="soft", color_scheme="gray"),
                    justify="between", 
                    align_items="center", 
                    width="100%",
                    flex_shrink=0, # Evita que el encabezado se encoja
                ),
                rx.divider(),
                
                # Cuerpo de los filtros con barra de desplazamiento
                rx.scroll_area(
                    rx.vstack(
                        # Filtro de Precio
                        rx.vstack(
                            rx.text("Precio", weight="bold"),
                            rx.input(placeholder="Mínimo", value=AppState.min_price, on_change=AppState.set_min_price, type="number"),
                            rx.input(placeholder="Máximo", value=AppState.max_price, on_change=AppState.set_max_price, type="number"),
                            spacing="2", 
                            align_items="start", 
                            width="100%"
                        ),

                        # Lógica condicional para mostrar filtros
                        rx.cond(
                            (AppState.current_category != "") & (AppState.current_category != "todos"),
                            # if: hay una categoría específica, muestra los filtros correspondientes
                            rx.cond(
                                AppState.current_category == Category.ROPA.value,
                                filtros_ropa,
                                rx.cond(
                                    AppState.current_category == Category.CALZADO.value,
                                    filtros_calzado,
                                    rx.cond(
                                        AppState.current_category == Category.MOCHILAS.value,
                                        filtros_mochilas,
                                        rx.fragment() # No muestra nada para otras categorías
                                    )
                                )
                            ),
                            # else: no hay categoría, muestra los filtros generales
                            filtros_generales
                        ),
                        spacing="4",
                        padding_right="1.5em", # Espacio para la barra de scroll
                        width="100%",
                    ),
                    type="auto", 
                    scrollbars="vertical",
                ),

                # Estilos del contenedor principal de la columna de filtros
                spacing="4",
                padding="1em",
                height="100%",
                width="280px",
                bg=rx.color("gray", 2),
            ),
            
            # Columna derecha: El botón para mostrar/ocultar el panel
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
        
        # Estilos para posicionar y animar todo el componente del panel
        height="95vh",
        max_height="800px",
        position="fixed",
        top="50%",
        left="0",
        transform=rx.cond(AppState.show_filters, "translateY(-50%)", "translate(-280px, -50%)"),
        transition="transform 0.3s ease-in-out",
        z_index=1000,
    )